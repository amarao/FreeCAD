import pytest
import mock


@pytest.fixture(scope="module")
def mock_FreeCAD():
    mock_params = mock.MagicMock()
    mock_params.ParamGet.return_value.GetString = \
        lambda x, y: y
    mock_params.ParamGet.return_value.GetFloat = \
        lambda x, y: y
    yield mock_params
    assert mock_params.ParamGet.call_args[0] ==  \
        ("User parameter:BaseApp/Preferences/Mod/Draft", )


@pytest.fixture(scope="module")
def mock_Draft():
    Draft = mock.MagicMock()
    Draft.svgpatterns.return_value = {
        'pattern_present': ['some_value']
    }
    return Draft


@pytest.fixture(scope="module")
def getSVG(mock_FreeCAD, mock_Draft):
    import sys
    with mock.patch.dict(sys.modules, {
            "FreeCAD": mock_FreeCAD,
            "DraftVecUtils": mock.MagicMock(),
            "WorkingPlane": mock.MagicMock(),
            "Part": mock.MagicMock(),
            "DraftGeomUtils": mock.MagicMock(),
            "Draft": mock_Draft
    }):
        import getSVG
        yield getSVG


def test_good_getDraftParam_svgDashedLine(getSVG):
    assert getSVG.getDraftParam('svgDashedLine', '1,1,1') == '1,1,1'


def test_good_getDraftParam_svgDiscretization(getSVG):
    assert getSVG.getDraftParam('svgDiscretization', 1.0) == 1.0


def test_sad_getDraftParam_svgDiscretization(getSVG):
    with pytest.raises(ValueError):
        getSVG.getDraftParam('foobar', "foobar")


@pytest.mark.parametrize("input, scale, out", [
    ("1,1,1", 1, "1.0,1.0,1.0"),  # trivial
    ("5,3,1", 2, "2.5,1.5,0.5"),  # division of integers
    ("0.1,0.2,-0.2", 2, "0.05,0.1,-0.1"),  # division of floats, negative
    ("0.0,0.0", 2, "0.0,0.0"),  # zero input, two numbers
])
def test_good_process_custom_linestyle(getSVG, input, scale, out):
    assert getSVG.process_custom_linestyle(input, scale) == out


def test_sad_process_custrom_linestyle_empty(getSVG):
    assert getSVG.process_custom_linestyle(None, 0) == 'none'
    assert getSVG.process_custom_linestyle('', 0) == 'none'


def test_sad_process_custrom_linestyle_no_coma(getSVG):
    assert getSVG.process_custom_linestyle("something", 0) == 'none'


def test_sad_process_custrom_linestyle_zero_scale(getSVG, capsys):
    assert getSVG.process_custom_linestyle("1,1", 0) == "none"
    assert "division by zero" in capsys.readouterr().out


def test_sad_process_custrom_linestyle_nan(getSVG, capsys):
    assert getSVG.process_custom_linestyle("NaN,1", 1) == "none"
    assert "Not a number" in capsys.readouterr().out


def test_sad_process_custrom_linestyle_inf(getSVG, capsys):
    assert getSVG.process_custom_linestyle("Inf,2", 1) == "none"
    assert "Not a number" in capsys.readouterr().out


def test_sad_process_custrom_linestyle_bad_string(getSVG, capsys):
    assert getSVG.process_custom_linestyle("one, two", 1) == "none"
    assert "could not convert string to float" in capsys.readouterr().out


def test_sad_process_custrom_linestyle_bad_type(getSVG, capsys):
    assert getSVG.process_custom_linestyle("1,2", None) == "none"
    assert "NoneType" in capsys.readouterr().out


def test_bad_process_custrom_linestyle_wrong_linestyle_type(getSVG):
    with pytest.raises(Exception):
        getSVG.process_custom_linestyle(dict, 1)


@pytest.mark.parametrize("input, scale, output", [
    ("Dashed", 1, "0.09,0.05"),  # known type
    ("Dashdot", 1, "0.09,0.05,0.02,0.05"),  # known type
    ("Dotted", 1, "0.02,0.02"),  # known type
    ("Dotted", 2, "0.02,0.02"),  # no division for known type
    ("1.0,2.0", 1, "1.0,2.0"),  # no changes with scale=1
    ("0.1,0.01", 10, "0.01,0.001"),  # scale
])
def test_good_getLineStyle(getSVG, input, scale, output):
    assert getSVG.getLineStyle(input, scale) == output


def test_sad_getLineStyle_bad_linestyle(getSVG):
    assert getSVG.getLineStyle("foobar", 2.0) == "none"


#  not test for getProj/getDiscretized yet

def test_good_getPattern_present(getSVG):
    assert getSVG.getPattern('pattern_present') == 'some_value'


def test_sad_getPattern_absent(getSVG):
    assert getSVG.getPattern('pattern_absent') == ''
