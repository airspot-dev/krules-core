import json

import pytest

import time
from multiprocessing import Process

from krules_core.providers import _testing_subject_storage_factory
from krules_core.subject import SubjectProperty, SubjectExtProperty, PropertyType


@pytest.fixture
def storage_subject1():
    return _testing_subject_storage_factory("subject1")


@pytest.fixture
def storage_subject2():
    return _testing_subject_storage_factory("subject2")


def test_factories(storage_subject1, storage_subject2):

    assert str(storage_subject1) != str(storage_subject2)

    assert str(_testing_subject_storage_factory("subject1")) == str(storage_subject1)


def test_property_kinds():

    prop_p = SubjectProperty("p")
    assert prop_p.value is None
    assert prop_p.type == PropertyType.DEFAULT
    prop_e = SubjectExtProperty("p")
    assert prop_e.type == PropertyType.EXTENDED

    # test simple value
    prop = SubjectProperty("p", 1)
    assert prop.json_value() == json.dumps(1)
    assert prop.get_value() == 1
    prop = SubjectExtProperty("p", 2)
    assert prop.get_value() == 2
    assert prop.json_value() == json.dumps(2)

    prop = SubjectProperty("p", lambda x: x*2)
    assert prop.json_value(2) == json.dumps(4)
    assert prop.get_value() == 4
    prop = SubjectExtProperty("p", lambda x: x.format(2))
    assert prop.get_value("value is {}") == "value is 2"
    assert prop.json_value("value is {}") == json.dumps("value is 2")


def test_load_store_and_flush(storage_subject1):

    props, ext_props = storage_subject1.load()

    assert props == {} and ext_props == {}

    storage_subject1.store(
        inserts=(
            SubjectProperty("p1", 1),
            SubjectProperty("p2", "2'3"),  # sql needs escape
            SubjectExtProperty("px1", 3),
            SubjectExtProperty("p1", "s1")
        )
    )

    props, ext_props = storage_subject1.load()

    assert len(props) == 2
    assert len(ext_props) == 2
    assert props["p1"] == 1
    assert props["p2"] == "2'3"
    assert ext_props["px1"] == 3
    assert ext_props["p1"] == "s1"

    storage_subject1.store(
        updates=(
            SubjectProperty("p2", 3),
            SubjectExtProperty("p1", "s2"),
        ),
        deletes=(
            SubjectProperty("p1"),
            SubjectExtProperty("px1"),
        )
    )

    props, ext_props = storage_subject1.load()

    assert len(props) == 1
    assert len(ext_props) == 1
    assert props["p2"] == 3
    assert ext_props["p1"] == "s2"

    storage_subject1.flush()

    props, ext_props = storage_subject1.load()

    assert props == {} and ext_props == {}


def test_multiple_subjects(storage_subject1, storage_subject2):

    storage_subject1.store(
        inserts=(
            SubjectProperty("p1", 1),
            SubjectProperty("p2", 2),
            SubjectExtProperty("p3", 3),
        )
    )
    storage_subject2.store(
        inserts=(
            SubjectProperty("p1", 1),
            SubjectExtProperty("p2", 2),
        )
    )

    props1, ext_props1 = storage_subject1.load()
    props2, ext_props2 = storage_subject2.load()

    assert len(props1) == 2
    assert len(ext_props1) == 1
    assert len(props2) == 1
    assert len(ext_props2) == 1

    storage_subject1.store(
        updates=(
            SubjectProperty("p1", 10),
            SubjectExtProperty("p3", 30)
        ),
        deletes=(
            SubjectProperty("p2"),
        )
    )

    props1, ext_props1 = storage_subject1.load()
    props2, ext_props2 = storage_subject2.load()

    assert len(props1) == 1
    assert len(props2) == 1
    assert len(ext_props2) == 1

    assert props1["p1"] == 10
    assert props2["p1"] == 1


def test_set_and_get(storage_subject1):

    with pytest.raises(AttributeError):
        storage_subject1.get(SubjectProperty("pset"))

    # simple value
    new_value, old_value = storage_subject1.set(SubjectProperty("pset", 1))
    assert old_value is None
    assert new_value == 1
    storage_subject1.delete(SubjectProperty("pset"))
    new_value, old_value = storage_subject1.set(SubjectProperty("pset", 1), 0)
    assert old_value == 0
    assert new_value == 1
    new_value, old_value = storage_subject1.set(SubjectProperty("pset", "1'2"))
    assert new_value == "1'2"
    assert old_value == 1

    assert storage_subject1.get(SubjectProperty("pset")) == "1'2"

    # computed value
    storage_subject1.set(SubjectProperty("pset", lambda x: x.replace("'", "$")))

    assert storage_subject1.get(SubjectProperty("pset")) == "1$2"

    # having exceptions in writing operations does not cause bad status (eg; write-locked database)
    with pytest.raises(Exception):
        storage_subject1.set(SubjectProperty("pset", lambda x: x/0))
    storage_subject1.set(SubjectProperty("psetX", 0))

    # test concurrency
    if storage_subject1.is_concurrency_safe():
        def _wait_and_incr(val):
            time.sleep(1)
            return val+1

        def _call_wait_and_incr():
            storage_subject1.set(SubjectProperty("psetX", _wait_and_incr))
        p = Process(target=_call_wait_and_incr)
        p.start()
        storage_subject1.set(SubjectProperty("psetX", lambda x: x+1))
        p.join()
        assert storage_subject1.get(SubjectProperty("psetX")) == 2


def test_incr_decr(storage_subject1):

    storage_subject1.flush()
    new_value, old_value = storage_subject1.incr(SubjectProperty("p"))
    assert new_value == 1
    assert old_value is None
    new_value, old_value = storage_subject1.incr(SubjectProperty("p"), 2)
    assert new_value == 3
    assert old_value == 1

    new_value, old_value = storage_subject1.decr(SubjectProperty("p"))
    assert new_value == 2
    assert old_value == 3
    new_value, old_value = storage_subject1.decr(SubjectProperty("p"), 2.1)
    assert round(new_value, 1) == -.1

    storage_subject1.delete(SubjectProperty("p"))
    new_value, old_value = storage_subject1.decr(SubjectProperty("p"))
    assert new_value == -1
    assert old_value is None
    with pytest.raises(TypeError):
        storage_subject1.incr(SubjectProperty("p"), "noway")



