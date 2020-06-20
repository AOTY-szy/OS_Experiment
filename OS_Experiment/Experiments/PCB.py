class PCB:
    def __init__(self, **kwargs):
        for item in kwargs.items():
            setattr(self, item[0], item[1])
