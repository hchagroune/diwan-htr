from .base import IMAGE_EXT, RemoteFile, Storage


def make_storage(settings) -> Storage:
    if settings.storage == "local":
        from .local import LocalStorage

        # local_folders lets two keys share one folder, e.g. {train_texts: train_images}
        return LocalStorage(settings.path(settings.local_root), settings.local_folders)
    from .gdrive import DriveStorage

    d = settings.drive
    return DriveStorage(d.folders, d.auth, settings.path(d.credentials_file), settings.path(d.token_file))


__all__ = ["IMAGE_EXT", "RemoteFile", "Storage", "make_storage"]
