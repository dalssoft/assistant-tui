from domain.steps.step import Step


class MessageCreationStep(Step):
    type = "message_creation"

    def __init__(self, thread_run, thread_run_step):
        super().__init__(thread_run, thread_run_step.id)
        self.thread_run_step = thread_run_step

    @staticmethod
    def is_type(step):
        return step.step_details.type == MessageCreationStep.type

    def message_id(self):
        return self.thread_run_step.step_details.message_creation.message_id

    def debug(self):
        return (
            super().debug()
            + f"""        
        | message_id: {self.message_id()}
        """
        )
