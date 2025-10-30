""" import os, shutil, io
from typing import ByteString

class StorageModel:
    @staticmethod
    def save_to_sshfs(img_bytes: ByteString, filename: str, sshfs_mount_path: str, dir_= "unclassified") -> bool:
        try:
            base_dir = os.path.normpath(sshfs_mount_path)
            destination_dir = os.path.join(base_dir, dir_)
            os.makedirs(destination_dir, exist_ok=True)

            destination_file = os.path.join(destination_dir, filename)
            with open(destination_file, "wb") as f:
                if isinstance(img_bytes, (bytes, bytearray)):
                    f.write(img_bytes)
                else:
                    data_stream = io.BytesIO(img_bytes)
                    shutil.copyfileobj(data_stream, f)
            return destination_file
        except Exception as e:
            raise """
            
import os, shutil, io, logging
from typing import ByteString, Optional
import paramiko

logger = logging.getLogger(__name__)

class StorageModel:
    @staticmethod
    def _ensure_remote_dirs(sftp: paramiko.SFTPClient, remote_dir: str):
        # crea directorios remotos recursivamente
        dirs = []
        head = remote_dir
        while head not in ('', '/'):
            dirs.append(head)
            head, _ = os.path.split(head)
        dirs = list(reversed(dirs))
        for d in dirs:
            try:
                sftp.stat(d)
            except IOError:
                try:
                    sftp.mkdir(d)
                except Exception:
                    # puede fallar si otro proceso crea la carpeta simultáneamente
                    pass

    @staticmethod
    def save_to_sshfs(img_bytes: ByteString, filename: str, sshfs_mount_path: str, dir_: str = "unclassified") -> str:
        """
        Intenta guardar localmente en sshfs_mount_path/dir_/filename.
        Devuelve la ruta completa del archivo local si tuvo éxito.
        Lanza FileNotFoundError si la ruta base no existe, y cualquier otra excepción si falla la escritura.
        """
        if not filename:
            raise ValueError("filename vacío.")
        if not sshfs_mount_path:
            raise ValueError("sshfs_mount_path vacío.")

        base_dir = os.path.normpath(sshfs_mount_path)

        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"Ruta de montaje no disponible desde este proceso: {base_dir}")

        destination_dir = os.path.join(base_dir, dir_)
        os.makedirs(destination_dir, exist_ok=True)

        destination_file = os.path.join(destination_dir, filename)

        with open(destination_file, "wb") as f:
            if isinstance(img_bytes, (bytes, bytearray)):
                f.write(img_bytes)
            else:
                data_stream = io.BytesIO(img_bytes)
                shutil.copyfileobj(data_stream, f)

        if not os.path.exists(destination_file):
            raise IOError(f"No se pudo verificar el archivo guardado: {destination_file}")

        return destination_file

    @staticmethod
    def save_to_sftp(img_bytes: ByteString,
                     filename: str,
                     remote_base_path: str,
                     dir_: str = "unclassified",
                     host: Optional[str] = None,
                     port: Optional[int] = None,
                     username: Optional[str] = None,
                     key_filename: Optional[str] = None,
                     timeout: int = 10) -> str:
        """
        Sube el archivo por SFTP a host:path. Devuelve la ruta remota completa (path en el servidor).
        Si key_filename es None intenta usar '~/.ssh/id_rsa' por defecto.
        """
        host = host or os.getenv("SFTP_HOST")
        port = int(port or os.getenv("SFTP_PORT", 22))
        username = username or os.getenv("SFTP_USER")
        key_filename = key_filename or os.getenv("SFTP_KEY_PATH") or os.path.expanduser("~/.ssh/id_rsa")

        if not host or not username:
            raise ValueError("Host o usuario SFTP no configurados.")

        remote_base = os.path.normpath(remote_base_path)
        remote_dir = os.path.join(remote_base, dir_).replace("\\", "/")
        remote_path = os.path.join(remote_dir, filename).replace("\\", "/")

        # Conectar y subir
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # intentar con llave privada
            try:
                client.connect(hostname=host, port=port, username=username, key_filename=key_filename, timeout=timeout)
            except Exception as e_key:
                # fallback: intentar sin key si hay agente/credenciales
                client.connect(hostname=host, port=port, username=username, timeout=timeout)

            sftp = client.open_sftp()
            try:
                StorageModel._ensure_remote_dirs(sftp, remote_dir)
                # abrir archivo remoto en modo write binario
                with sftp.file(remote_path, "wb") as remote_file:
                    if isinstance(img_bytes, (bytes, bytearray)):
                        remote_file.write(img_bytes)
                    else:
                        data_stream = io.BytesIO(img_bytes)
                        shutil.copyfileobj(data_stream, remote_file)
                # permisos opcionales: sftp.chmod(remote_path, 0o644)
            finally:
                sftp.close()
                client.close()
            return remote_path
        except Exception as e:
            logger.exception("SFTP upload failed")
            raise

    @staticmethod
    def save(img_bytes: ByteString,
             filename: str,
             sshfs_mount_path: str,
             dir_: str = "unclassified",
             use_sftp_fallback: bool = True,
             sftp_config: Optional[dict] = None) -> str:
        """
        Intenta guardar localmente; si falla y use_sftp_fallback es True, intenta SFTP
        sftp_config puede incluir host, port, username, key_filename.
        Devuelve la ruta (local o remota) donde quedó el archivo.
        """
        try:
            return StorageModel.save_to_sshfs(img_bytes, filename, sshfs_mount_path, dir_=dir_)
        except Exception as e:
            logger.warning("Fallo guardando localmente: %s. Intentando SFTP si está habilitado.", e)
            if not use_sftp_fallback:
                raise
            cfg = sftp_config or {}
            return StorageModel.save_to_sftp(img_bytes,
                                             filename,
                                             remote_base_path=cfg.get("remote_base", sshfs_mount_path),
                                             dir_=dir_,
                                             host=cfg.get("host"),
                                             port=cfg.get("port"),
                                             username=cfg.get("username"),
                                             key_filename=cfg.get("key_filename"))