PYTHON_BIN := $(CURDIR)/.venv/bin/python

.PHONY: backend frontend stack stop-backend stop-frontend stack-stop stack-restart

backend:
	cd backend && PYTHONUNBUFFERED=1 $(PYTHON_BIN) -m backend.main

frontend:
	cd frontend && npm run dev

stack:
	$(MAKE) -j2 backend frontend

stop-backend:
	-pkill -f "backend.main" || true

stop-frontend:
	-pkill -f "next dev -p 3002" || true

stack-stop: stop-backend stop-frontend

stack-restart: stack-stop
	$(MAKE) stack

