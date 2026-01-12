# GP Account Transfer

CLI tool to **transfer an existing account to a new username**, updating databases and server files.
Useful for renames, merges, or account migrations (Java / Bedrock).

---

## Requirements

- Python 3.9+
- Database access
- Read/write permissions on the server path

---

## Configuration

Create a `.env` file in the project root.

```env
STORAGE_TYPE="mysql" # mysql, postgresql, mongodb | none for disable

# Note: no database name is required; all accessible databases are scanned.
DATABASE_HOST="127.0.0.1"
DATABASE_PORT="3306"
DATABASE_USERNAME="root"
DATABASE_PASSWORD=""

SERVER_PATH="/path/to/server" # absolute path (use \ for windows)

BEDROCK_FORMAT=".{username}"

BACKUP_ENABLED=false # set to true on production enviroment
BACKUP_PATH="" # empty = "./backup"
```

---

# Usage
## Premium / Cracked
```
python3 transfer.py --old-name oldName --new-name newName
```
## Bedrock
```
python main.py --old-name OldPlayer --new-name NewPlayer --bedrock
```

---

# Arguments doc
| Argument | Required | Description
|:----------:|:-------------:|:------:|
| `--old-name` | yes | Old player username|
|`--new-name` | yes | New player username |
| `--bedrock` | no | Enable Bedrock username formatting |
| `--dry-run` | no | Enable dry-run mode (no changes are written) |

---

# License

This project is licensed under the MIT License.

You are free to:
- use the software for any purpose
- modify the source code
- distribute copies
- include it in commercial or private projects

Under the following conditions:
- the original copyright notice and license text must be included
- the software is provided **"as is"**, without warranty of any kind

The authors are not responsible for any damage, data loss, or misuse.

See the `LICENSE` file for the full license text.
