# gen_vectordb
Generate VectorDB from input


## Install requirements.

```
pip install -r requirements.txt
```

## Prepare course materials.
Create a directory under `./scratch` dir. Directory name must be all CAPITAL.

Example directory names.
- `RNR355`
- `CYVERSE`


## Run

```
python3 ./create_vectordb.py --no_download [course_name]
```

For example:
```
python3 ./create_vectordb.py --no_download RNR355
```

To capture intermediate documents, add `--create_docs`:
```
python3 ./create_vectordb.py --no_download --create_docs RNR355
```
