# kalcal.dataset.sky_models attributes
from pkg_resources import resource_filename

# Antenna tables made by Sphe on `simms` package (KERN)
# See: https://github.com/ratt-ru/simms/tree/master/simms/observatories

KAT7 = resource_filename(
    'kalcal', 'datasets/antenna_tables/kat-7.itrf.txt')

LOFAR = resource_filename(
    'kalcal', 'datasets/antenna_tables/lofar_ml.itrf.txt')

MEERKAT = resource_filename(
    'kalcal', 'datasets/antenna_tables/meerkat.itrf.txt'))

SKA197 = resource_filename(
    'kalcal', 'datasets/antenna_tables/skamid197.itrf.txt')

SKA254 = resource_filename(
    'kalcal', 'datasets/antenna_tables/skamid254.itrf.txt')

VLAA = resource_filename(
    'kalcal', 'datasets/antenna_tables/vlaa.itrf.txt')

VLAB = resource_filename(
    'kalcal', 'datasets/antenna_tables/vlab.itrf.txt')

VLAC = resource_filename(
    'kalcal', 'datasets/antenna_tables/vlac.itrf.txt')

VLAD = resource_filename(
    'kalcal', 'datasets/antenna_tables/vlad.itrf.txt')

WSRT = resource_filename(
    'kalcal', 'datasets/antenna_tables/wsrt.itrf.txt')


def list_antenna_tables():
    """List all antenna tables allowed for empty ms creation."""

    output = """
    ===> Implemented antenna-tables for `create_empty_ms` command:
    ===> kat7, lofar, meerkat, ska197, ska254, vlaa, vlab, vlac, vlad, wsrt   
    """

    print(output)