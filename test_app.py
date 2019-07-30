from apistar import test

from app import app, cars, CAR_NOT_FOUND

client = test.TestClient(app)


def test_list_cars():
    response = client.get('/')
    assert response.status_code == 200

    json_resp = response.json()
    assert len(json_resp) == 1000

    expected = {"id": 1,
                "make": "Pontiac",
                "model": "Aztek",
                "year": 2003,
                "vin": "WAUGFAFR9AA688873"}
    assert json_resp[0] == expected


def test_create_car():
    data = {'make': 'BMW',
            'model': '535xi',
            'year': 2008}

    response = client.post('/', data=data)
    assert response.status_code == 201
    assert len(cars) == 1001

    response = client.get('/1001/')
    expected = {'id': 1001, 'make': 'BMW',
                'model': '535xi', 'year': 2008, 'vin': ''}
    assert response.json() == expected

    data = {'make': 'Lotus',
            'model': 'some_other_model',
            'year': 2019,
            'vin': 123}
    response = client.post('/', data=data)
    assert response.status_code == 201
    expected = {'id': 1002, 'make': 'Lotus',
                'model': 'some_other_model', 'year': 2019,
                'vin': '123'}

    response = client.get('/1002/')
    assert response.json() == expected
    assert len(cars) == 1002


def test_create_car_missing_fields():
    data = {'key': 1}
    response = client.post('/', data=data)
    assert response.status_code == 400

    errors = response.json()
    assert errors['make'] == 'The "make" field is required.'
    assert errors['model'] == 'The "model" field is required.'
    assert errors['year'] == 'The "year" field is required.'


def test_create_car_field_validation():
    data = {'make': 'Opel',
            'model': 'x'*51,
            'year': 2051}
    response = client.post('/', data=data)
    assert response.status_code == 400

    errors = response.json()
    assert "Must be one of" in errors['make']
    assert errors['model'] == 'Must have no more than 50 characters.'
    assert errors['year'] == 'Must be less than or equal to 2050.'


def test_get_car():
    response = client.get('/777/')
    assert response.status_code == 200

    expected = {"id": 777,
                "make": "Ford",
                "model": "Windstar",
                "year": 1995,
                "vin": "WBAAV53471F892809"}
    assert response.json() == expected


def test_get_car_notfound():
    response = client.get('/11111/')
    assert response.status_code == 404
    assert response.json() == {'error': CAR_NOT_FOUND}


def test_update_car():
    data = {'make': 'Honda',
            'model': 'some_model',
            'year': 2018}
    response = client.put('/777/', data=data)
    assert response.status_code == 200

    # test put response
    expected = {'id': 777, 'make': 'Honda',
                'model': 'some_model', 'year': 2018, 'vin': ''}
    assert response.json() == expected

    # check if data persisted == wiped out previous data car 777
    response = client.get('/777/')
    assert response.json() == expected


def test_update_car_notfound():
    data = {'make': 'Honda',
            'model': 'some_model',
            'year': 2018}
    response = client.put('/11111/', data=data)

    assert response.status_code == 404
    assert response.json() == {'error': CAR_NOT_FOUND}


def test_update_car_validation():
    data = {'make': 'nonsense',
            'model': 's' * 51,
            'year': 1899}
    response = client.put('/777/', data=data)
    assert response.status_code == 400

    errors = response.json()
    assert "Must be one of" in errors['make']
    assert errors['year'] == 'Must be greater than or equal to 1900.'
    assert errors['model'] == 'Must have no more than 50 characters.'


def test_delete_car():
    car_count = len(cars)

    for i in (11, 22, 33):
        response = client.delete(f'/{i}/')
        assert response.status_code == 204

        response = client.get(f'/{i}/')
        assert response.status_code == 404  # car gone

    assert len(cars) == car_count - 3
