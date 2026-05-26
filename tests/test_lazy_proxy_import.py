"""
Tests that fhir_server_proxy (and its kubernetes dependency) is only imported
when CONNECTOR_MODE=HAPI_FHIR_SERVER_PROXY, not at application startup.

The root cause of the original bug was an unconditional top-level import of
fhir_server_proxy in app.py, which triggered kubernetes.config.load_incluster_config()
at module load time and raised ConfigException outside of a Kubernetes cluster.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root and src/* dirs are importable when tests are run via
# `python -m pytest` from the repo root.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
for _p in (_ROOT, _SRC, os.path.join(_SRC, "providers"), os.path.join(_SRC, "utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _make_failing_k8s_config() -> MagicMock:
    """Return a mock kubernetes.config whose both loader methods raise."""
    mock_cfg = MagicMock()
    mock_cfg.load_kube_config.side_effect = Exception("no kubeconfig file found")
    mock_cfg.load_incluster_config.side_effect = Exception(
        "kubernetes.config.config_exception.ConfigException: not running inside a cluster"
    )
    return mock_cfg


def _base_patches(extra: dict | None = None) -> dict:
    """Return a sys.modules patch dict that stubs out all modules that are
    either not installed in the test environment (git, flask, pick) or that
    would pull in unwanted side-effects (the connector submodules themselves).

    The connector submodules are mocked so that ``app.py``'s top-level
    ``from connectors_modes import git_fsh, ...`` does not trigger their
    transitive imports (which would fail on missing packages like GitPython).
    """
    connector_mocks: dict = {
        name: MagicMock()
        for name in (
            "connectors_modes",
            "connectors_modes.git_fsh",
            "connectors_modes.fhir_server_sync",
            "connectors_modes.delete_resources",
            "connectors_modes.smm_tool",
        )
    }
    # Packages missing from this environment
    absent_packages: dict = {
        name: MagicMock()
        for name in ("git", "flask", "flask.json", "pick")
    }
    patches = {**connector_mocks, **absent_packages}
    if extra:
        patches.update(extra)
    return patches


class TestLazyProxyImport(unittest.TestCase):
    """Verify fhir_server_proxy is only imported on-demand."""

    def _purge_app_modules(self) -> None:
        """Remove app and fhir_server_proxy from sys.modules to allow re-import."""
        for key in list(sys.modules):
            if key == "app" or "fhir_server_proxy" in key:
                del sys.modules[key]

    def setUp(self):
        self._purge_app_modules()

    def tearDown(self):
        self._purge_app_modules()

    def test_fhir_server_proxy_not_imported_at_app_load(self):
        """fhir_server_proxy must NOT appear in sys.modules when app is imported."""
        with patch.dict(
            sys.modules,
            _base_patches({"kubernetes.config": _make_failing_k8s_config()}),
        ):
            import app  # noqa: F401

            # Check inside the context: patch.dict restores sys.modules on exit,
            # so any module added by the import is still present here.
            loaded = [k for k in sys.modules if "fhir_server_proxy" in k]

        self.assertEqual(
            loaded,
            [],
            f"fhir_server_proxy was imported eagerly at module load. "
            f"It should only be imported for HAPI_FHIR_SERVER_PROXY mode. "
            f"Found in sys.modules: {loaded}",
        )

    def test_kubernetes_config_not_called_when_importing_app(self):
        """kubernetes.config loader methods must not be called during app import."""
        failing_cfg = _make_failing_k8s_config()

        with patch.dict(sys.modules, _base_patches({"kubernetes.config": failing_cfg})):
            try:
                import app  # noqa: F401
            except Exception as exc:
                self.fail(
                    f"Importing app raised an unexpected exception, likely caused by "
                    f"an eager import of fhir_server_proxy triggering kubernetes config "
                    f"loading: {exc}"
                )

        failing_cfg.load_kube_config.assert_not_called()
        failing_cfg.load_incluster_config.assert_not_called()

    def test_importing_app_does_not_raise_config_exception(self):
        """Importing app must succeed even when kubernetes is completely unavailable."""
        mock_kubernetes = MagicMock()
        mock_kubernetes.config = _make_failing_k8s_config()

        with patch.dict(
            sys.modules,
            _base_patches(
                {
                    "kubernetes": mock_kubernetes,
                    "kubernetes.client": MagicMock(),
                    "kubernetes.config": mock_kubernetes.config,
                }
            ),
        ):
            try:
                import app  # noqa: F401
            except Exception as exc:
                self.fail(
                    f"Importing app raised ConfigException or similar: {exc}"
                )


if __name__ == "__main__":
    unittest.main()
