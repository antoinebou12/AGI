class Tasks:
    def __init__(self, task_id, task_name, task_description, task_status):
        self.task_id = task_id
        self.task_name = task_name
        self.task_description = task_description
        self.task_status = task_status

    def create_task(self, task_name, task_description, task_status):
        """Create a task"""
        return Tasks(task_name, task_description, task_status)

    def list_tasks(self):
        """List all tasks"""
        return Tasks

    def delete_task(self, task_id):
        """Delete a task"""
        return Tasks

    def update_task(self, task_id, task_name, task_description, task_status):
        """Update a task"""
        return Tasks
