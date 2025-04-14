import pytest


@pytest.fixture(autouse=True)
def add_requirement(request):
    if hasattr(pytest, 'mark'):
        req_id = request.node.get_closest_marker('requirement')
        if req_id:
            pytest.mark.requirement(req_id.args[0])(request.function)
