import pygame


class EventHandler:
    def __init__(self, event_handlers):
        self.event_handlers = event_handlers

    def handle_events(self, evt_queue):
        for evt in evt_queue:
            if self.has_handler_for(evt):
                self.event_handlers[evt.type](evt)

    def has_handler_for(self, evt):
        return evt.type in self.event_handlers
