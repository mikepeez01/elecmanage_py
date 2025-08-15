import paramiko
import os
import datetime
import json

def download_sftp_files(host, port, username, password, remote_dir, local_dir, record_path):
    os.makedirs(local_dir, exist_ok=True)

    # Load previous record of downloaded files and timestamps
    if os.path.exists(record_path):
        with open(record_path, 'r') as f:
            downloaded_files = json.load(f)
    else:
        downloaded_files = {}

    # Connect to SFTP
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        print(f"Conectando a {host}:{port} como {username}...")
        for attr in sftp.listdir_attr(remote_dir):
            file_name = attr.filename
            remote_path = f"{remote_dir}/{file_name}"
            local_path = os.path.join(local_dir, file_name)
            mod_time = attr.st_mtime

            # Check if file is new or modified
            prev_mod_time = downloaded_files.get(file_name)
            if prev_mod_time is None or mod_time > prev_mod_time:
                print(f"Descargando '{file_name}'...")
                sftp.get(remote_path, local_path)
                downloaded_files[file_name] = mod_time
                print(f"Guardado en: {local_path}")
            # else:
            #     print(f"'{file_name}' no ha cambiado. Se omite.")

    finally:
        sftp.close()
        transport.close()
        print(f"Conexión cerrada para {host}:{port}.")

    # Save updated record
    with open(record_path, 'w') as f:
        json.dump(downloaded_files, f, indent=2)
