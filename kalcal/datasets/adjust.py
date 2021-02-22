import packratt
import kalcal
import os

def packratt_registry_append():
    mpath = packratt.__file__[:-11]
    path1 = os.path.join(mpath, 'conf', 'registry.yaml')

    mpath = kalcal.__file__[:-11]
    path2 = os.path.join(mpath, 'custom_registry.yaml')

    with open(path1, 'a') as OUT:        
        OUT.write('\n')
        with open(path2, 'r') as IN:
            lines = IN.readlines()
            if len(lines) <= 21:
                print("DONE")
                OUT.writelines(lines)