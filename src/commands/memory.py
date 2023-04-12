from commands.command import BaseCommand


class MemoryAddCommand(BaseCommand):
    def execute(self):
        self.add_memory(self.arguments[0])

    def commit_memory(self, string):
        """Commit a string to memory"""
        _text = f"""Committing memory with string "{string}" """
        mem.permanent_memory.append(string)
        return _text

    def delete_memory(self, key):
        """Delete a memory with a given key"""
        if 0 <= key < len(mem.permanent_memory):
            _text = f"Deleting memory with key {str(key)}"
            del mem.permanent_memory[key]
            print(_text)
            return _text
        else:
            print("Invalid key, cannot delete memory.")
            return None

    def overwrite_memory(self, key, string):
        """Overwrite a memory with a given key and string"""
        # Check if the key is a valid integer
        if isinstance(key, int):
            # Check if the integer key is within the range of the permanent_memory list
            if 0 <= key < len(mem.permanent_memory):
                _text = f"Overwriting memory with key {str(key)} and string {string}"
                return self._extracted_from_overwrite_memory_9(string, key, _text)
            else:
                print(f"Invalid key '{key}', out of range.")
                return None
        elif isinstance(key, str):
            _text = f"Overwriting memory with key {key} and string {string}"
            return self._extracted_from_overwrite_memory_9(string, key, _text)
        else:
            print(f"Invalid key '{key}', must be an integer or a string.")
            return None

    # TODO Rename this here and in `overwrite_memory`
    def _extracted_from_overwrite_memory_9(self, string, key, _text):
        # Overwrite the memory slot with the given integer key and string
        mem.permanent_memory[key] = string
        print(_text)
        return _text
