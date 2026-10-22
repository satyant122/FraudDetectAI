import os
import httpx
import streamlit as st

_in_process_client = None


def _get_in_process_client():
    global _in_process_client
    if _in_process_client is None:
        try:
            from starlette.testclient import TestClient
            from app.main import app

            _in_process_client = TestClient(app, raise_server_exceptions=False)
        except Exception as e:
            st.warning(f"Could not initialize local in-process client: {e}")
            return None
    return _in_process_client


def api(method, path, **kwargs):
    base_url = os.getenv("BANKING_API_URL", "http://localhost:8000").rstrip("/")
    timeout = 1.5 if "localhost" in base_url or "127.0.0.1" in base_url else 30.0

    # 1. Try external HTTP server first
    try:
        response = httpx.request(method, base_url + path, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", "Request failed")
        except ValueError:
            detail = "Request failed"
        st.error(str(detail))
        return None
    except httpx.RequestError:
        # 2. Fall back to in-process FastAPI client (e.g. for Streamlit Cloud or standalone UI)
        client = _get_in_process_client()
        if client is not None:
            try:
                resp = client.request(method, path, **kwargs)
                if resp.status_code >= 400:
                    try:
                        detail = resp.json().get("detail", "Request failed")
                    except Exception:
                        detail = resp.text
                    st.error(str(detail))
                    return None
                return resp.json()
            except Exception as exc:
                st.error(f"In-process banking API error: {exc}")
                return None

        st.error(
            "Banking API unavailable. Start `PYTHONPATH=src:. uvicorn app.main:app --reload` and run migrations."
        )
    return None
