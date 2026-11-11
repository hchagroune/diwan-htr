"""Google Drive API v3 storage.

Auth modes
  oauth            personal Gmail: one-time browser login, token cached in secrets/token.json
  service_account  Workspace Shared Drives (service accounts have no quota in personal "My Drive",
                   so they cannot create the output .txt files there)
"""
from __future__ import annotations

import io
import os
from pathlib import Path

from .base import GOOGLE_DOC, RemoteFile, Storage

SCOPES = ["https://www.googleapis.com/auth/drive"]
_FIELDS = "nextPageToken, files(id, name, mimeType, md5Checksum, modifiedTime, size)"


def _credentials(auth: str, credentials_file: Path, token_file: Path):
    if auth == "refresh_token":  # hosted servers: client id/secret + refresh token from environment secrets
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        missing = [k for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN") if not os.environ.get(k)]
        if missing:
            raise RuntimeError("Missing Google Drive secrets: " + ", ".join(missing))
        creds = Credentials(None, refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
                            token_uri="https://oauth2.googleapis.com/token",
                            client_id=os.environ["GOOGLE_CLIENT_ID"],
                            client_secret=os.environ["GOOGLE_CLIENT_SECRET"], scopes=SCOPES)
        creds.refresh(Request())
        return creds
    if auth == "service_account":
        from google.oauth2 import service_account

        return service_account.Credentials.from_service_account_file(str(credentials_file), scopes=SCOPES)

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES) if token_file.exists() else None
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not credentials_file.exists():
            raise FileNotFoundError(
                f"OAuth client file not found: {credentials_file}. "
                "Create a 'Desktop app' OAuth client in Google Cloud Console and save it there."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
        creds = flow.run_local_server(port=0)
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _q_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


class DriveStorage(Storage):
    def __init__(self, folders: dict, auth: str, credentials_file: Path, token_file: Path, service=None):
        self.folders = folders
        if service is None:
            from googleapiclient.discovery import build

            creds = _credentials(auth, Path(credentials_file), Path(token_file))
            service = build("drive", "v3", credentials=creds, cache_discovery=False)
        self.svc = service

    def _folder(self, key: str) -> str:
        fid = self.folders.get(key, "")
        if not fid or fid.startswith("PASTE_"):
            raise ValueError(f"Drive folder id for '{key}' is not set in config.yaml")
        return fid

    def list(self, folder_key: str) -> list[RemoteFile]:
        q = (f"'{self._folder(folder_key)}' in parents and trashed = false "
             "and mimeType != 'application/vnd.google-apps.folder'")
        out, token = [], None
        while True:
            resp = self.svc.files().list(
                q=q, fields=_FIELDS, pageSize=1000, pageToken=token,
                supportsAllDrives=True, includeItemsFromAllDrives=True,
            ).execute(num_retries=3)
            for f in resp.get("files", []):
                out.append(RemoteFile(
                    id=f["id"], name=f["name"], mime=f.get("mimeType", ""), md5=f.get("md5Checksum"),
                    modified=f.get("modifiedTime"), size=int(f["size"]) if f.get("size") else None,
                ))
            token = resp.get("nextPageToken")
            if not token:
                return out

    def download(self, file: RemoteFile) -> bytes:
        from googleapiclient.http import MediaIoBaseDownload

        if file.mime == GOOGLE_DOC:  # transcription kept as a Google Doc -> export as plain text
            request = self.svc.files().export_media(fileId=file.id, mimeType="text/plain")
        else:
            request = self.svc.files().get_media(fileId=file.id, supportsAllDrives=True)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request, chunksize=8 * 1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk(num_retries=3)
        return buf.getvalue()

    def _find(self, folder_id: str, name: str) -> str | None:
        q = f"name = '{_q_escape(name)}' and '{folder_id}' in parents and trashed = false"
        resp = self.svc.files().list(q=q, fields="files(id)", pageSize=1, supportsAllDrives=True,
                                     includeItemsFromAllDrives=True).execute(num_retries=3)
        files = resp.get("files", [])
        return files[0]["id"] if files else None

    def upload_text(self, folder_key: str, name: str, text: str) -> str:
        from googleapiclient.http import MediaIoBaseUpload

        folder_id = self._folder(folder_key)
        media = MediaIoBaseUpload(io.BytesIO(text.encode("utf-8")), mimetype="text/plain", resumable=False)
        existing = self._find(folder_id, name)
        if existing:  # overwrite instead of creating a second file with the same name
            self.svc.files().update(fileId=existing, media_body=media, supportsAllDrives=True).execute(num_retries=3)
            return existing
        body = {"name": name, "parents": [folder_id], "mimeType": "text/plain"}
        resp = self.svc.files().create(body=body, media_body=media, fields="id",
                                       supportsAllDrives=True).execute(num_retries=3)
        return resp["id"]

    def put(self, folder_key: str, name: str, data: bytes, mime: str = "application/octet-stream") -> RemoteFile:
        from googleapiclient.http import MediaIoBaseUpload

        folder_id = self._folder(folder_key)
        media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime, resumable=len(data) > 5 * 1024 * 1024)
        fields = "id, name, mimeType, md5Checksum, modifiedTime, size"
        existing = self._find(folder_id, name)
        if existing:
            f = self.svc.files().update(fileId=existing, media_body=media, fields=fields,
                                        supportsAllDrives=True).execute(num_retries=3)
        else:
            f = self.svc.files().create(body={"name": name, "parents": [folder_id]}, media_body=media,
                                        fields=fields, supportsAllDrives=True).execute(num_retries=3)
        return RemoteFile(id=f["id"], name=f.get("name", name), mime=f.get("mimeType", mime), md5=f.get("md5Checksum"),
                          modified=f.get("modifiedTime"), size=int(f["size"]) if f.get("size") else None)

    def copy_into(self, file: RemoteFile, folder_key: str, name: str | None = None) -> str:
        folder_id = self._folder(folder_key)
        name = name or file.name
        existing = self._find(folder_id, name)
        if existing:
            return existing
        resp = self.svc.files().copy(fileId=file.id, body={"name": name, "parents": [folder_id]},
                                     fields="id", supportsAllDrives=True).execute(num_retries=3)
        return resp["id"]
