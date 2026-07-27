from . import core_bp


@core_bp.route("/")
def index():
    return {
        "application": "CDCS Enterprise Management Platform",
        "version": "0.1.0-alpha",
        "status": "Running",
    }


@core_bp.route("/health")
def health():
    return {
        "status": "Healthy"
    }