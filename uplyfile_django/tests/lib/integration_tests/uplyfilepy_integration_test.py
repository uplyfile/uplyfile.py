import pytest, re
from uplyfile_django.lib.uplyfilepy import UplyImage
from urllib.parse import urlparse


""" Integration tests """


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


list_of_nums_for_filters = [
    ("0", "0"),
    ("1", "1"),
    ("-1", "-1"),
    ("15", "15"),
    ("50", "50"),
    ("75", "75"),
    ("101", "101"),
    ("999999", "999999"),
    ("-20", "-20"),
    ("-100", "-100"),
    ("-999999", "-999999"),
]

resize_crop_fit_format_avatar_list_of_params = [
    ("1000h", "h1000", "950", "950", "900", "900", "jpg", ".jpg", "300", "300"),
    ("h900", "h900", "850", "850", "800", "800", "bmp", ".bmp", "250", "250"),
    ("h800", "h800", "750", "750", "700", "700", "jpeg", ".jpeg", "200", "200"),
    (
        "-1000h",
        "h-1000",
        "-950",
        "-950",
        "-900",
        "-900",
        "webp",
        ".webp",
        "-300",
        "-300",
    ),
    ("-900h", "h-900", "-850", "-850", "-800", "-800", "png", ".png", "-250", "-250"),
    ("-800h", "h-800", "-750", "-750", "-700", "-700", "tiff", ".tiff", "-200", "-200"),
    ("h0", "h0", "0", "0", "0", "0", "tif", ".tif", "0", "0"),
    ("h0", "h0", "0", "0", "0", "0", "jp2", ".jp2", "0", "0"),
]

fit_crop_rotate_bg_color_face_crop_list_of_params = [
    ("1000", "1000", "90", "90", "black", "black", "1:align"),
    ("900", "900", "180", "180", "yellow", "yellow", "2:align"),
    ("800", "800", "270", "270", "32CD32", "32CD32", "1:align"),
    ("-1000", "-1000", "-90", "-90", "magenta", "magenta", "-1:align"),
    ("-900", "-900", "-180", "-180", "lightblue", "lightblue", "-2:align"),
    ("-800", "-800", "-270", "-270", "chocolate", "chocolate", "-1:align"),
    ("0", "0", "0", "0", "violet", "violet", "0:align"),
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


""" Multi operation testing without values and duplications [3 - 4 operations]"""


def test_avatar_blur_progressive_format_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.avatar().blur().progressive().format().url
        == f"{base_link}avatar,blur,progressive/{picture_name}"
    )


def test_median_bilateral_sharpen_autocontrast_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.median().bilateral().sharpen().autocontrast().url
        == f"{base_link}median,bilateral,sharpen,autocontrast/{picture_name}"
    )


# api don't support - bug
def test_black_and_white_invert_avatar_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.black_and_white().invert().avatar().url
        == f"{base_link}bw,invert,avatar/{picture_name}"
    )


def test_pixelate_enhance_mono_without_values(picture_object, base_link, picture_name):
    assert (
        picture_object.pixelate().enhance().mono().url
        == f"{base_link}pixelate,enhance,mono/{picture_name}"
    )


# upside down after flip & autorotate
def test_golden_mirror_flip_autorotate_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.golden().mirror().flip().autorotate().url
        == f"{base_link}golden,mirror,flip,autorotate/{picture_name}"
    )


def test_face_mark_download_sharpen_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.face_mark().download().sharpen().url
        == f"{base_link}face_mark,download,sharpen/{picture_name}"
    )


""" Multi operation testing without values and duplications [ > 4 operations]"""


def test_avatar_blur_progressive_format_median_bilateral_sharpen_autocontrast_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.avatar()
        .blur()
        .progressive()
        .format()
        .median()
        .bilateral()
        .sharpen()
        .autocontrast()
        .url
        == f"{base_link}avatar,blur,progressive,median,bilateral,sharpen,autocontrast/{picture_name}"
    )


def test_black_and_white_invert_avatar_pixelate_enhance_mono_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.black_and_white()
        .invert()
        .avatar()
        .pixelate()
        .enhance()
        .mono()
        .url
        == f"{base_link}bw,invert,avatar,pixelate,enhance,mono/{picture_name}"
    )


def test_golden_mirror_flip_autorotate_face_mark_download_sharpen_without_values(
    picture_object, base_link, picture_name
):
    assert (
        picture_object.golden()
        .mirror()
        .flip()
        .autorotate()
        .face_mark()
        .download()
        .sharpen()
        .url
        == f"{base_link}golden,mirror,flip,autorotate,face_mark,download,sharpen/{picture_name}"
    )


""" Multi operation testing with values and without duplications [3 - 4 operations]

            Filters and quality
"""


@pytest.mark.parametrize("test_input, expected", list_of_nums_for_filters)
def test_quality_blur_median_bilateral_with_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.quality(test_input)
        .blur(test_input)
        .median(test_input)
        .bilateral(test_input)
        .url
        == f"{base_link}quality:{expected},blur:{expected},median:{expected},bilateral:{expected}/{picture_name}"
    )


@pytest.mark.parametrize("test_input, expected", list_of_nums_for_filters)
def test_sharpen_autocontrast_pixelate_with_values(
    picture_object, base_link, picture_name, test_input, expected
):
    assert (
        picture_object.sharpen(test_input)
        .autocontrast(test_input)
        .pixelate(test_input, test_input, test_input)
        .url
        == f"{base_link}sharpen:{expected},autocontrast:{expected},pixelate:{expected}:{expected}:{expected}/{picture_name}"
    )


"""         Faces, resizings, formats"""


@pytest.mark.parametrize(
    "resize_input, resize_expected, crop_input, crop_expected, fit_input, fit_expected, format_input, format_expected, avatar_input, avatar_expected",
    resize_crop_fit_format_avatar_list_of_params,
)
def test_resize_crop_fit_avatar_format_with_values(
    picture_object,
    base_link,
    picture_name_without_extension,
    resize_input,
    resize_expected,
    crop_input,
    crop_expected,
    fit_input,
    fit_expected,
    format_input,
    format_expected,
    avatar_input,
    avatar_expected,
):
    assert (
        picture_object.resize(resize_input)
        .crop(crop_input, crop_input)
        .fit(fit_input, fit_input)
        .format(format_input)
        .avatar(avatar_input)
        .url
        == f"{base_link}resize:{resize_expected},crop:{crop_expected}:{crop_expected},fit:{fit_expected}:{fit_expected},avatar:{avatar_expected}/{picture_name_without_extension}{format_expected}"
    )


"""         Faces, resizings, bg, rotations"""


@pytest.mark.parametrize(
    "fit_crop_input, fit_crop_expected, rotate_input, rotate_expected, bg_color_input, bg_color_expected, face_crop_value_input_and_expected",
    fit_crop_rotate_bg_color_face_crop_list_of_params,
)
def test_fit_crop_rotate_bg_color_face_crop(
    picture_object,
    base_link,
    picture_name,
    fit_crop_input,
    fit_crop_expected,
    rotate_input,
    rotate_expected,
    bg_color_input,
    bg_color_expected,
    face_crop_value_input_and_expected,
):
    assert (
        picture_object.fit_crop(fit_crop_input, fit_crop_input)
        .rotate(rotate_input)
        .bg_color(bg_color_input)
        .face_crop(face_crop_value_input_and_expected)
        .url
        == f"{base_link}fit_crop:{fit_crop_expected}:{fit_crop_expected},rotate:{rotate_expected},bg_color:{bg_color_expected},face_crop:{face_crop_value_input_and_expected}/{picture_name}"
    )
