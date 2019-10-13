
class RpiBoard:



    def __init__(self):
        self._observers = []
        pass


    def _motion_detected(self):
        #assure that video is not streamed
        self.notify_observers()

    def _notify_observers(self):
        for observer in self._observers:
            observer()

    def add_observer(self, observer):
        self._observers.append(observer)

