class Dispatcher:
    def __init__(self, URI):
        self.URI = URI
        
    def get_URI(self):
        return self.URI
    
    #@abstractmethod
    def dispatch(self, data):
        pass