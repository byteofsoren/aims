import os

import yaml


class ConfigManager(object):

    """Docstring for load_config. """

    path: str = ''
    config: dict = dict()
    usefile = False

    def __init__(self, file_path=''):
        """TODO: to be defined. """
        if file_path:
            self.usefile = True
            self.path = file_path
            print(self.path)
            self._load_config()
            if self.config is None:
                raise Exception("Configuration not loaded")

    def __getitem__(self, key):
        return self.config.get(key, None)

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save()

    def __delitem__(self, key):
        if key in self.config:
            del self.config[key]
            self.save()

    def __len__(self):
        return len(self.config.keys())

    def _load_config(self):
        """
        Loads the self.path if it not is empty then it just creates the
        dict inside memory to be written later.
        """
        if os.path.exists(self.path) and os.path.isfile(self.path):
            # If the file has zero content
            if os.stat(self.path).st_size == 0:
                self.config = dict()
                return

            # Load the file
            try:
                with open(self.path, 'r') as file:
                    self.config = yaml.safe_load(file)
            except Exception as e:
                print(f"Error loading {self.path}: {e}")
                return {}
        elif os.path.exists(self.path) and not os.path.isfile(self.path):
            raise Exception(f"Path was not a file {self.path}")

    def keys(self):
        return self.config.keys()

    def values(self):
        """
        Returns the values from the self.config dict.
        :returns: self.config.values()

        """
        return self.config.values()
        pass

    def save(self):
        """
        Saves the self.config dict to the self.path
        And if the diretory strutcure do not exits it creates it.
        """
        directory_path = os.path.dirname(self.path)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        try:
            with open(self.path, 'w') as file:
                yaml.dump(self.config, file)
        except Exception as e:
            print(f"Error writing {self.path}: {e}")
            return {}
