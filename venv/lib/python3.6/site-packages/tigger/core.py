import hashlib, os.path, string, tigger.error

_valid_tag_characters = (
        set(string.ascii_letters) |
        set(string.digits) |
        set([".", "-", "_", " "])
        )

_meta_dir_name = ".tigger-meta"

def initialize_base_dir(base_dir="."):
    base_dir = os.path.abspath(base_dir)
    os.makedirs(os.path.join(base_dir, _meta_dir_name, "files"))
    os.makedirs(os.path.join(base_dir, _meta_dir_name, "tags"))

def find_base_dir(start_dir="."):
    base_dir = os.path.abspath(start_dir)
    while not os.path.isdir(os.path.join(base_dir, _meta_dir_name)):
        if os.path.dirname(base_dir) == base_dir:  # can't go up
            raise tigger.error.NotInTaggedDir(start_dir)
        base_dir = os.path.dirname(base_dir)
    return base_dir

def is_valid_tag(tag):
    if len(tag) == 0:
        return False
    elif len(set(list(tag)) - _valid_tag_characters) == 0:
        return True
    else:
        return False

def tag_to_hash(tag):
    if not is_valid_tag(tag):
        raise tigger.error.InvalidTag(tag)
    return hashlib.sha1(tag.encode("utf-8")).hexdigest()

def tag_to_metapath(tag):
    hash = tag_to_hash(tag)
    return os.path.join(find_base_dir(),
            _meta_dir_name,
            "tags",
            hash[:2],
            tag)

def file_path_normalize(name):
    file_path = os.path.abspath(name)
    if not file_path.startswith(find_base_dir()):
        raise tigger.error.NotInTaggedDir(file_path)
    else:
        return file_path.replace(find_base_dir(), "", 1)

def file_to_metapath(name):
    hash = hashlib.sha1(name.encode("utf-8")).hexdigest()
    return os.path.join(find_base_dir(),
            _meta_dir_name,
            "files",
            hash[:2])

def _file_update_tags(name, tags, action="add", propagate=False):
    tags = [tag.strip() for tag in tags]

    for tag in tags:
        if not is_valid_tag(tag):
            raise tigger.error.InvalidTag(tag)

    sought_file = file_path_normalize(name)
    tags_filename = file_to_metapath(sought_file)
    file_tag_map = {}

    try:
        with open(tags_filename, "r") as tags_file:
            for line in tags_file:
                try:
                    file_name, old_tags = line.split("\0")
                except:
                    continue

                old_tags = [tag.strip() for tag in old_tags.split(",")]
                if old_tags == [""]:
                    old_tags = []

                if file_name == sought_file:
                    if action == "add":
                        new_tag_set = set(old_tags) | set(tags)
                    elif action == "remove":
                        new_tag_set = set(old_tags) - set(tags)
                    else:
                        raise ValueError("Invalid operation: {}".format(action))

                    if new_tag_set == set(old_tags):
                        return
                    else:
                        file_tag_map[file_name] = sorted(new_tag_set)
                else:
                    file_tag_map[file_name] = sorted(old_tags)
    except:  # file simply doesn't exist yet
        if action == "add":
            file_tag_map[sought_file] = sorted(set(tags))

    with open(tags_filename, "w") as tags_file:
        for file_name in sorted(file_tag_map.keys()):
            if file_tag_map[file_name] != []:
                tags_file.write("{}\0{}\n".format(file_name,
                    ",".join(file_tag_map[file_name])))

    if propagate:
        for tag in tags:
            _tag_update_files(tag, [name], action)

def file_get_tags(name):
    sought_file = file_path_normalize(name)
    try:
        with open(file_to_metapath(sought_file), "r") as tags_file:
            for line in tags_file:
                try:
                    file_name, tags = line.split("\0")
                except ValueError:
                    continue

                tags = [tag.strip() for tag in tags.split(",")]

                if file_name == sought_file:
                    if tags == [""]:
                        tags = []
                    return tags
            return []
    except IOError as e:
        if e.errno == 2:  # no such file, assume no tags
            return []
        else:
            raise e

def file_add_tags(name, tags):
    return _file_update_tags(name, tags, "add", True)

def file_remove_tags(name, tags):
    return _file_update_tags(name, tags, "remove", True)

def _tag_update_files(tag, names, action="add", propagate=False):
    tag = tag.strip()
    set_names = set([file_path_normalize(name) for name in names])

    tag_filename = tag_to_metapath(tag)
    tagged_files = set()

    try:
        with open(tag_filename, "r") as tag_file:
            for line in tag_file:
                if line.strip() != "":
                    tagged_files.add(line.strip())
    except IOError:
        pass  # tag doesn't exist, so we'll just be creating it

    if action == "add":
        tagged_files |= set_names
    elif action == "remove":
        tagged_files -= set_names

    try:
        os.makedirs(os.path.dirname(tag_filename))  # in case even the dir doesn't exist
    except:
        pass

    with open(tag_filename, "w") as tag_file:
        for name in sorted(tagged_files):
            tag_file.write("{}\n".format(name))

    if propagate:
        for name in names:
            _file_update_tags(name, [tag], action)

def tag_get_files(tag, rel_paths=False):
    tagged_files = set()

    try:
        with open(tag_to_metapath(tag), "r") as tag_file:
            for line in tag_file:
                # TODO: create relative paths from the absolute ones when
                # requested
                tagged_files.add(find_base_dir() + line.strip())
    except IOError as e:
        if e.errno == 2:  # no such file, assume no tags
            return []
        else:
            raise e

    return sorted(tagged_files)

def tag_add_files(tag, names):
    return _tag_update_files(tag, names, "add", True)

def tag_remove_files(tag, names):
    return _tag_update_files(tag, names, "remove", True)
