class ApuChannelPhase:
    def __init__(self, stepLength=0, stepHeight=0, stepCount=1, stepWay=1):
        self.stepLength = stepLength
        self.stepHeight = stepHeight
        self.stepCount = stepCount
        self.stepWay = stepWay

    def __str__(self):
        return f"ChannelPhase#{id(self)}(stepLength={self.stepLength}, stepHeight={self.stepHeight}, stepCount={self.stepCount}, stepWay={self.stepWay})"
