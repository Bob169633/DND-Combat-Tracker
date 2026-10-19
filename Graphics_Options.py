from pathlib import Path


SUPPORTED_IMAGE_EXTENSIONS = {
  ".jpg",
  ".jpeg",
  ".png",
  ".webp"
}


def get_project_folder():
  return Path(__file__).resolve().parent


def get_graphics_folder():
  return get_project_folder() / "graphics"


def get_graphics_images():
  graphics_folder = get_graphics_folder()

  if not graphics_folder.exists():
    return []

  images = []

  for path in graphics_folder.iterdir():
    if not path.is_file():
      continue

    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
      continue

    images.append(path)

  return sorted(
    images,
    key=lambda path: path.name.lower()
  )


def get_image_display_name(path):
  path = Path(path)
  name = path.stem.replace("_", " ").replace("-", " ")
  return name.title()


def saveable_image_path(path):
  path = Path(path).resolve()
  project_folder = get_project_folder().resolve()

  try:
    relative = path.relative_to(project_folder)
    return relative.as_posix()
  except ValueError:
    return str(path)


def resolve_image_path(path):
  if not path:
    return None

  path = Path(path)

  if path.is_absolute():
    return path

  return get_project_folder() / path
