TEST_DATA = {
    'user_table': [
        {
            'id': '8330971b-88c7-4e7e-927f-a3776ee33b4f',
            'name': 'Erich',
            'surname': 'Gamma',
            'birthday': '1980-01-01T00:00:00Z',
            'email': 'erich.gamma@example.com',
            'password': 'ErichGammaPassword',
            'created_at': '2023-01-01T00:00:00Z',
            'updated_at': '2023-01-01T00:00:00Z',
            'created': '2023-01-01T00:00:00',
        },
        {
            'id': '9996d2d5-cac8-4139-a234-beca94489757',
            'name': 'Richard',
            'surname': 'Helm',
            'birthday': '1980-01-01T00:00:00Z',
            'email': 'richard.helm@example.com',
            'password': 'RichardHelmPassword',
            'created_at': '01-02-2023',
            'updated_at': '01-02-2023',
            'created': '2023-01-01T00:00:00',
        },
        {
            'id': '1dca7406-09d4-4f29-8a20-bce3048ce133',
            'name': 'Ralph',
            'surname': 'Johnson',
            'birthday': '1980-01-03T00:00:00Z',
            'email': 'ralph.johnson@example.com',
            'password': 'RalphJohnsonPassword',
            'created_at': '2023-01-03T00:00:00Z',
            'updated_at': '2023-01-03T00:00:00Z',
            'created': '2023-01-01T00:00:00',
        },
    ],
    'role': [
        {
            'id': '8a59eba0-2fa5-4e16-a63d-62f61ccf705e',
            'name': 'Anonymous',
            'created': '2023-01-01T00:00:00',
        },
        {
            'id': 'd01b6317-8ee3-47e1-9836-81f458b0d70a',
            'name': 'Registered',
            'created': '2023-01-01T00:00:00',
        },
        {
            'id': 'b9a801db-22bf-4b23-84e7-f446bb06c156',
            'name': 'Subscribed',
            'created': '2023-01-01T00:00:00',
        },
        {
            'id': 'b3ce986a-3ded-4899-91fd-1371cb2fd165',
            'name': 'Moderator',
            'created': '2023-01-01T00:00:00',
        },
        {
            'id': '194ee160-e06c-4b6a-b3f9-3e46a4d7344f',
            'name': 'Admin',
            'created': '2023-01-01T00:00:00',
        },
    ],
    'user_role': [
        {
            'id': '5c64bee7-5d33-412b-b8f5-00b9444fab30',
            'user_id': '8330971b-88c7-4e7e-927f-a3776ee33b4f',
            'role_name': 'Registered',
        },
        {
            'id': '44cca078-cd47-42dd-aaf4-eefaf68d58d3',
            'user_id': '9996d2d5-cac8-4139-a234-beca94489757',
            'role_name': 'Subscribed',
        },
        {
            'id': '981ef108-4177-49eb-ac46-e2f5f8ee03e8',
            'user_id': '9996d2d5-cac8-4139-a234-beca94489757',
            'role_name': 'Moderator',
        },
        {
            'id': '409a4609-aa2f-4bd8-b4a5-27bf81cd5b76',
            'user_id': '1dca7406-09d4-4f29-8a20-bce3048ce133',
            'role_name': 'Admin',
        },
    ],
    'refresh_session': [
        {
            'id': '5099cef7-0a2d-4dc6-86df-6b2e4482d845',
            'finger_print': 'desktop_user_1',
            'user_id': '8330971b-88c7-4e7e-927f-a3776ee33b4f',
            'refresh_token': '5099cef7-0a2d-4dc6-86df-6b2e4482d845',
            'expires_at': '01-01-2024',
            'created_at': '2023-01-03T00:00:00Z',
            'created': '01-01-2023',
        },
        {
            'id': '1c1309d3-0305-4120-ba70-41d6571ba3ef',
            'finger_print': 'mobile_user_1',
            'user_id': '8330971b-88c7-4e7e-927f-a3776ee33b4f',
            'refresh_token': '1c1309d3-0305-4120-ba70-41d6571ba3ef',
            'expires_at': '01-02-2023',
            'created_at': '2023-01-03T00:00:00Z',
            'created': '01-02-2023',
        },
        {
            'id': 'c46be0e3-083a-4016-a593-d551a30a3648',
            'finger_print': 'desktop_user_2',
            'user_id': '9996d2d5-cac8-4139-a234-beca94489757',
            'refresh_token': 'c46be0e3-083a-4016-a593-d551a30a3648',
            'expires_at': '01-03-2023',
            'created_at': '2023-01-03T00:00:00Z',
            'created': '01-03-2023',
        },
        {
            'id': '7b5ff2bb-6a20-4ee5-ba40-e44f4e25c6b7',
            'finger_print': 'desktop_user_3',
            'user_id': '1dca7406-09d4-4f29-8a20-bce3048ce133',
            'refresh_token': '7b5ff2bb-6a20-4ee5-ba40-e44f4e25c6b7',
            'expires_at': '01-04-2023',
            'created_at': '2023-01-03T00:00:00Z',
            'created': '01-04-2023',
        },
    ],
    'login_history': [
        {
            'id': 'ca070b83-c819-4652-877f-b89f03441d52',
            'agent_id': '5099cef7-0a2d-4dc6-86df-6b2e4482d845',
            'time': '2023-02-03T00:00:00',
            'action': 'login',
        },
        {
            'id': '0018e83f-0907-478c-bfd6-43d6eb3348a6',
            'agent_id': '5099cef7-0a2d-4dc6-86df-6b2e4482d845',
            'time': '2023-03-03T00:00:00',
            'action': 'logout',
        },
        {
            'id': 'd5212c4f-c6de-423e-b5ce-0ac3e7f07393',
            'agent_id': '1c1309d3-0305-4120-ba70-41d6571ba3ef',
            'time': '2023-04-03T00:00:00',
            'action': 'login',
        },
        {
            'id': 'e05545b1-b5d0-45b4-a054-70c0f1136926',
            'agent_id': 'c46be0e3-083a-4016-a593-d551a30a3648',
            'time': '2023-05-03T00:00:00',
            'action': 'login',
        },
        {
            'id': '986bccc7-64cd-4eee-aa9a-a56c20037420',
            'agent_id': '7b5ff2bb-6a20-4ee5-ba40-e44f4e25c6b7',
            'time': '2023-06-03T00:00:00',
            'action': 'login',
        },
    ],
}

post_roles = [{
    "id": "423d2ea0-2fa5-4e16-a63d-62f61ccf705e",
    "name": "Hero",
    "created": "2023-01-01T00:00:00"
},
    {
        "id": "8a52d4f2-2fa5-12da-a63d-62f61ccf705e",
        "name": "Greed",
        "created": "2023-01-01T00:00:00"
    },
]
