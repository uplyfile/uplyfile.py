import pytest
import re
from uplyfile_django.lib.uplyfilepy import UplyImage
from urllib.parse import urlparse


""" Unit tests """

list_of_nums = [
    ("0", 0),
    ("1", 1),
    ("-1", -1),
    ("12345", 12345),
    ("97213", 97213),
    ("21", 21),
    ("99990", 99990),
    ("9", 9),
]

format_list = [
    ("jpg", ".jpg"),
    ("bmp", ".bmp"),
    ("jpeg", ".jpeg"),
    ("webp", ".webp"),
    ("png", ".png"),
    ("tiff", ".tiff"),
    ("tif", ".tif"),
    ("jp2", ".jp2"),
]

resize_list = [
    ("100h", "h100"),
    ("h100", "h100"),
    ("h1", "h1"),
    ("1h", "h1"),
    ("-1h", "h-1"),
    ("0h", "h0"),
    ("1000h", "h1000"),
    ("h1000", "h1000"),
    ("w20", "w20"),
    ("w200", "w200"),
    ("200w", "w200"),
    ("w0", "w0"),
]

list_of_quality = [
    ("lightest", "lightest"),
    ("lighter", "lighter"),
    ("normal", "normal"),
    ("high", "high"),
    ("highest", "highest"),
    ("0", "0"),
    ("1000", "1000"),
    ("1000", "1000"),
    ("20", "20"),
    ("200", "200"),
    ("200", "200"),
    ("0", "0"),
]


list_crop_with_two_values = [
    ("100", "100"),
    ("1000", "1000"),
    ("1", "1"),
    ("-1", "-1"),
    ("-100", "-100"),
    ("0", "0"),
    ("10000", "10000"),
    ("100000", "100000"),
    ("20", "20"),
    ("200", "200"),
    ("200", "200"),
]

list_crop_with_three_values = [
    ("100", "100", "center"),
    ("100", "100", "center"),
    ("1", "1", "center"),
    ("1", "1", "center"),
    ("-1", "-1", "center"),
    ("0", "0", "center"),
    ("1000", "1000", "center"),
    ("1000", "1000", "center"),
    ("20", "20", "center"),
    ("200", "200", "center"),
    ("200", "200", "center"),
    ("0", "0", "center"),
]


list_of_colors = [
    ("black", "black"),
    ("yellow", "yellow"),
    ("32CD32", "32CD32"),
    ("magenta", "magenta"),
    ("lightblue", "lightblue"),
    ("chocolate", "chocolate"),
    ("2d5391", "2d5391"),
    ("violet", "violet"),
]


list_resize_with_two_values = [
    ("100", "100"),
    ("100", "100"),
    ("1", "1"),
    ("1", "1"),
    ("-1", "-1"),
    ("0", "0"),
    ("1000", "1000"),
    ("1000", "1000"),
    ("20", "20"),
    ("200", "200"),
    ("200", "200"),
    ("0", "0"),
]

list_of_urls = [
    "https://uplycdn.com/Cjii6o/YVJ5M0LSOhXn/20180614_160625.jpg",
    "https://uplycdn.com/docs/bvAbyJOsjafM/girls-smiling.jpg",
    "https://uplycdn.com/docs/bvAbyJOsjafM/face_mark,download,sharpen/girls-smiling.jpg"
    "https://uplycdn.com/docs/bvAbyJOsjafM/sharpen,blur,quality:100,autorotate,autoformat,blur,blur/girls-smiling.jpg"
    "https://uplycdn.com/Cjii6o/kb2CqsjPai2u/2019-01-29-23.2201.jpg",
    "https://uplycdn.com/Cjii6o/kb2CqsjPai2u/avatar,sharpen,bw/",
    "https://uplycdn.com/docs/bvAbyJOsjafM/avatar,sharpen,bw/",
    "https://uplycdn.com/Cjii6o/kb2CqsjPai2u/",
    "https://uplycdn.com/docs/bvAbyJOsjafM/",
    "https://uplycdn.com/Cjii6o/YVJ5M0LSOhXn/",
]


@pytest.fixture(params=list_of_urls)
def image_url(request):
    return request.param


@pytest.fixture
def picture_object(image_url):
    return UplyImage(image_url)


@pytest.fixture
def base_link(image_url):
    parse = urlparse(image_url)
    start, stop = re.match(r"/\w+/\w+/", parse.path).span()
    return f"{parse.scheme}://{parse.netloc}" + parse.path[start:stop]


@pytest.fixture
def picture_name(image_url):
    return image_url.rpartition("/")[-1]


@pytest.fixture
def picture_name_without_extension(image_url):
    pic_name = image_url.rpartition("/")[-1]
    return pic_name.rpartition(".")[0]


@pytest.fixture
def url_path(image_url):
    return urlparse(image_url).path


@pytest.fixture
def re_pattern():
    return r"^/\w+/\w+/"


def test_raise_if_invalid_url(re_pattern, url_path):
    assert re.match(re_pattern, url_path).string == url_path


def test_avatar_without_arg(picture_object, base_link, picture_name):
    assert picture_object.avatar().url == f"{base_link}avatar/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_avatar_with_arg_eval(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.avatar(test_input).url
        == f"{base_link}avatar:{expected}/{picture_name}"
    )


def test_face_mark(picture_object, base_link, picture_name):
    assert picture_object.face_mark().url == f"{base_link}face_mark/{picture_name}"


def test_face_crop_without_arg(picture_object, base_link, picture_name):
    assert picture_object.face_crop().url == f"{base_link}face_crop/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_face_crop_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.face_crop(test_input).url
        == f"{base_link}face_crop:{expected}/{picture_name}"
    )


def test_face_crop_with_align(picture_object, base_link, picture_name):
    assert (
        picture_object.face_crop("align").url
        == f"{base_link}face_crop:align/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_face_crop_with_value_and_align(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.face_crop(test_input, "align").url
        == f"{base_link}face_crop:{expected}:align/{picture_name}"
    )


def test_autoformat(picture_object, base_link, picture_name):
    assert picture_object.autoformat().url == f"{base_link}autoformat/{picture_name}"


def test_download(picture_object, base_link, picture_name):
    assert picture_object.download().url == f"{base_link}download/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_quality)
def test_quality_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.quality(test_input).url
        == f"{base_link}quality:{expected}/{picture_name}"
    )


def test_progressive(picture_object, base_link, picture_name):
    assert picture_object.progressive().url == f"{base_link}progressive/{picture_name}"


def test_blur_without_value(picture_object, base_link, picture_name):
    assert picture_object.blur().url == f"{base_link}blur/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_blur_with_value(picture_object, base_link, picture_name, test_input, expected):
    assert (
        picture_object.blur(test_input).url
        == f"{base_link}blur:{expected}/{picture_name}"
    )


def test_median_without_arg(picture_object, base_link, picture_name):
    assert picture_object.median().url == f"{base_link}median/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_median_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.median(test_input).url
        == f"{base_link}median:{expected}/{picture_name}"
    )


def test_bilateral(picture_object, base_link, picture_name):
    assert picture_object.bilateral().url == f"{base_link}bilateral/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_bilateral_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.bilateral(test_input).url
        == f"{base_link}bilateral:{expected}/{picture_name}"
    )


def test_sharpen_without_arg(picture_object, base_link, picture_name):
    assert picture_object.sharpen().url == f"{base_link}sharpen/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_sharpen_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.sharpen(test_input).url
        == f"{base_link}sharpen:{expected}/{picture_name}"
    )


def test_autocontrast(picture_object, base_link, picture_name):
    assert (
        picture_object.autocontrast().url == f"{base_link}autocontrast/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_autocontrast_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.autocontrast(test_input).url
        == f"{base_link}autocontrast:{expected}/{picture_name}"
    )


def test_black_and_white(picture_object, base_link, picture_name):
    assert picture_object.black_and_white().url == f"{base_link}bw/{picture_name}"


def test_invert(picture_object, base_link, picture_name):
    assert picture_object.invert().url == f"{base_link}invert/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_duotone_with_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.duotone(test_input, test_input).url
        == f"{base_link}duotone:{expected}:{expected}/{picture_name}"
    )


def test_pixelate_withour_args(picture_object, base_link, picture_name):
    assert picture_object.pixelate().url == f"{base_link}pixelate/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_pixelate_with_one_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.pixelate(test_input).url
        == f"{base_link}pixelate:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_pixelate_with_two_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.pixelate(test_input, test_input).url
        == f"{base_link}pixelate:{expected}:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_pixelate_with_three_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.pixelate(test_input, test_input, test_input).url
        == f"{base_link}pixelate:{expected}:{expected}:{expected}/{picture_name}"
    )


def test_enhance(picture_object, base_link, picture_name):
    assert picture_object.enhance().url == f"{base_link}enhance/{picture_name}"


def test_mono(picture_object, base_link, picture_name):
    assert picture_object.mono().url == f"{base_link}mono/{picture_name}"


def test_golden(picture_object, base_link, picture_name):
    assert picture_object.golden().url == f"{base_link}golden/{picture_name}"


@pytest.mark.parametrize("test_input, expected", resize_list)
def test_resize_with_one_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.resize(test_input).url
        == f"{base_link}resize:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_resize_with_two_values)
def test_resize_with_two_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.resize(test_input, test_input).url
        == f"{base_link}resize:{expected}:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_crop_with_two_values)
def test_crop_with_two_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.crop(test_input, test_input).url
        == f"{base_link}crop:{expected}:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected, align", list_crop_with_three_values)
def test_crop_with_three_values(
    picture_object, base_link, picture_name, test_input, expected, align
):
    assert (
        picture_object.crop(test_input, test_input, align).url
        == f"{base_link}crop:{expected}:{expected}:{align}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_crop_with_four_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.crop(test_input, test_input, test_input, test_input).url
        == f"{base_link}crop:{expected}:{expected}:{expected}:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_fit_with_two_args(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.fit(test_input, test_input).url
        == f"{base_link}fit:{expected}:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_fit_crop_with_two_args(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.fit_crop(test_input, test_input).url
        == f"{base_link}fit_crop:{expected}:{expected}/{picture_name}"
    )


def test_rotate_without_value(picture_object, base_link, picture_name):
    assert picture_object.rotate().url == f"{base_link}rotate/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_nums)
def test_rotate_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.rotate(test_input).url
        == f"{base_link}rotate:{expected}/{picture_name}"
    )


def test_mirror(picture_object, base_link, picture_name):
    assert picture_object.mirror().url == f"{base_link}mirror/{picture_name}"


def test_autorotate(picture_object, base_link, picture_name):
    assert picture_object.autorotate().url == f"{base_link}autorotate/{picture_name}"


@pytest.mark.parametrize("test_input, expected", list_of_colors)
def test_bg_color_with_value(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.bg_color(test_input).url
        == f"{base_link}bg_color:{expected}/{picture_name}"
    )


def test_format_without_arg(picture_object, base_link, picture_name):
    assert picture_object.format().url == base_link + picture_name


@pytest.mark.parametrize("test_input, expected", format_list)
def test_format_with_value(
    picture_object, base_link, picture_name_without_extension, test_input, expected
):
    assert (
        picture_object.format(test_input).url
        == f"{base_link}{picture_name_without_extension}{expected}"
    )


@pytest.mark.parametrize("test_input, expected", format_list)
def test_multi_format_with_value(
    picture_object, base_link, picture_name_without_extension, test_input, expected
):
    assert (
        picture_object.format(test_input)
        .format(test_input)
        .format(test_input)
        .format(test_input)
        .url
        == f"{base_link}{picture_name_without_extension}{expected}"
    )


@pytest.mark.parametrize("test_input, expected", format_list)
def test_multi_format_with_and_without_values_as_last(
    picture_object, base_link, picture_name_without_extension, test_input, expected
):
    assert (
        picture_object.format().format(test_input).format(test_input).format().url
        == f"{base_link}{picture_name_without_extension}{expected}"
    )


@pytest.mark.parametrize("test_input, expected", format_list)
def test_multi_format_with_and_without_values(
    picture_object, base_link, picture_name_without_extension, test_input, expected
):
    assert (
        picture_object.format()
        .format(test_input)
        .format(test_input)
        .format()
        .format(test_input)
        .url
        == f"{base_link}{picture_name_without_extension}{expected}"
    )
