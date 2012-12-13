import transaction
from celery.task import Task


class SqlAlchemyTask(Task):

    ignore_result = True
    logname = None
    session_class = None

    def process(session, *args, **kwargs):
        raise NotImplementedError()

    def run(self, *args, **kwargs):
        rv = None
        session = self.session_class()
        try:
            rv = self.process(session, *args, **kwargs)
        except Exception:
            raise
            # getLogger(self.logname).error('error in task %s(*%r,**%r)' %
            #            (self.name, args, kwargs), exc_info=True)
            # Error Queue here for retry jobs here ?
        transaction.commit()
        return rv
