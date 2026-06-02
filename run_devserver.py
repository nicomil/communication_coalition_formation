#!/usr/bin/env python
"""
Avvia il server oTree dopo aver applicato i patch per compatibilità Starlette.
- Patch 1: ExceptionMiddleware in starlette.exceptions (oTree lo importa da lì).
  Solo se manca, usa starlette.middleware.exceptions.ExceptionMiddleware E
  aggiunge _lookup_exception_handler se assente (richiesto da otree/patch.py).
- Patch 2: build_middleware_stack per Middleware (cls, args, kwargs) in Starlette >= 0.40.
Esegue devserver_inner direttamente (nessun subprocess) così i patch restano attivi.
"""
import sys

# Patch 1: prima di importare oTree
import starlette.exceptions
try:
    import starlette.middleware.exceptions as mw_exc
except ImportError:
    mw_exc = None

if not hasattr(starlette.exceptions, 'ExceptionMiddleware'):
    if mw_exc is not None and hasattr(mw_exc, 'ExceptionMiddleware'):
        starlette.exceptions.ExceptionMiddleware = mw_exc.ExceptionMiddleware

# Garantire che la classe usata da oTree abbia _lookup_exception_handler (richiesto da otree/patch.py)
_ExceptionMiddleware = getattr(starlette.exceptions, 'ExceptionMiddleware', None)
if _ExceptionMiddleware is not None and not hasattr(_ExceptionMiddleware, '_lookup_exception_handler'):
    def _lookup_exception_handler(self, exc):
        handlers = getattr(self, '_exception_handlers', None)
        if handlers is None:
            return None
        for cls in type(exc).__mro__:
            if cls in handlers:
                return handlers[cls]
        return None
    _ExceptionMiddleware._lookup_exception_handler = _lookup_exception_handler

# Import oTree dopo il patch 1
import otree.asgi as asgi_module
from starlette.middleware import Middleware

# Patch 2: build_middleware_stack (Middleware in Starlette nuova restituisce (cls, args, kwargs))
def build_middleware_stack_patched(self):
    debug = self.debug
    error_handler = None
    exception_handlers = {}
    for key, value in self.exception_handlers.items():
        if key in (500, Exception):
            error_handler = value
        else:
            exception_handlers[key] = value
    middlewares = [
        Middleware(asgi_module.middleware.CommitTransactionMiddleware),
        Middleware(asgi_module.OTreeServerErrorMiddleware, handler=error_handler, debug=debug),
        Middleware(asgi_module.middleware.PerfMiddleware),
        Middleware(asgi_module.middleware.SessionMiddleware, secret_key=asgi_module.middleware._SECRET),
        Middleware(asgi_module.ExceptionMiddleware, handlers=exception_handlers, debug=debug),
    ]
    app = self.router
    for m in reversed(middlewares):
        parts = list(m)
        if len(parts) == 2:
            cls, options = parts
            app = cls(app=app, **options)
        else:
            cls, args, kwargs = parts
            app = cls(app=app, *args, **kwargs)
    return app

asgi_module.OTreeStarlette.build_middleware_stack = build_middleware_stack_patched

# Avvia devserver_inner direttamente (stesso processo, niente subprocess)
if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '8000'
    sys.argv = ['otree', 'devserver_inner', str(port)]
    from otree.main import execute_from_command_line
    execute_from_command_line()
