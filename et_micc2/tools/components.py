import json
import os
from pathlib import Path
from types import SimpleNamespace

import et_micc2.tools.utils as utils

class ComponentDatabase:
    def __init__(self, project_path):
        self.project_path = project_path
        self.deserialize()


    def deserialize(self):
        """Read file ``db.json`` into self.db."""

        components_json = self.project_path / 'components.json'
        try:
            with components_json.open('r') as f:
                self.db = json.load(f)
        except FileNotFoundError:
            # for backward compatibility: if there is a db.json file rename it and retry
            db_json = self.project_path / 'db.json'
            try:
                db_json.rename(components_json)
                self.deserialize()
            except FileNotFoundError:
                self.db = {}


    def serialize(self, new_components=[], logger=None, verbose=False):
        """Insert components and write self.db to file ``db.json``.

        Params:
            values: list of components to insert before serializing.
        """
        # components[i].context is a SimpleNamespace object which is not default json serializable.
        # This function takes care of that by converting to `str` where possible, and
        # ignoring objects that do not need serialization, as e.g. self.context.logger.

        if not isinstance(new_components,list):
            new_components = [new_components]
        new_components = [component for component in new_components if not component is None]
        if not self.db and not new_components:
            return

        for component in new_components:
            # produce a json serializable version of db_entry['context']:
            serializable_context = {}
            context = component['context']
            if isinstance(context, SimpleNamespace):
                context = context.__dict__
            for key, val in context.items():
                if isinstance(val, (dict, list, tuple, str, int, float, bool)):
                    # default serializable types
                    serializable_context[key] = val
                    if verbose:
                        print(f"serialize_db: using ({key}:{val})")
                elif isinstance(val, Path):
                    serializable_context[key] = str(val)
                    if verbose:
                        print(f"serialize_db: using ({key}:str('{val}'))")
                else:
                    if verbose:
                        print(f"serialize_db: ignoring ({key}:{val})")
            component_key = context['add_name']
            component['context'] = serializable_context

            if not hasattr(self, 'db'):
                # Read db.json into self.db if self.db does not yet exist.
                self.deserialize()

            # Update the database:
            if logger:
                logger.info(f"Updating database entry for : '{component_key}'")
            self.db[component_key] = component

        # finally, serialize self.db

        if logger:
            logger.info(f"Serializing components database.")
        with utils.in_directory(self.project_path):
            with open('components.json', 'w') as f:
                json.dump(self.db, f, indent=2)


    def has_name(self, name) -> str:

        """Is there a component with name <name>. Returns the relative path of the component as a str."""
        name = str(name)
        if os.sep in name:
            name = Path(name).name
        for key,v in self.db.items():
            k_name = Path(key).name
            if name == k_name:
                return key
        return ''


    def similar_to(self, name: str) -> list:
        """Return all components containing name."""
        similar = []
        for key,v in self.db.items():
            if name in key:
                similar.append(key)
        return similar

    ## forwarding methods
    def __getitem__(self, key):
        return self.db.__getitem__(key)

    def __delitem__(self, key):
        self.db.__delitem__(key)

    def __contains__(self, key):
        return self.db.__contains__(key)