import logging

logging.basicConfig(
    level=logging.INFO,
    filemode="a",  # append
    filename="assistant.log",
    format="[%(asctime)s:%(levelname)s:%(name)s]%(message)s",
)


def log(*messages):
    logging.info("\n".join(str(message) for message in messages))


def log_action(instance, action, *messages):
    if isinstance(instance, str):
        # instance is a string (ex: "Thread") then it's a class name
        instance_name = instance
    else:
        # instance is the self of the class
        instance_name = instance.__class__.__name__

        # check if instance has an id
        if hasattr(instance, "id"):
            instance_name += f":id={instance.id}"

    logging.info(
        f"[{instance_name}:{action}]" + "\n".join(str(message) for message in messages)
    )
