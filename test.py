

if __name__ == '__main__':
    steps = [
        {
            "id": 1
        },
        {
            "id": 2
        },
        {
            "id": 3
        }
    ]
    steps_ids = [1, 4]
    for step_id in steps_ids:
        result = list(filter(lambda step: step['id'] == step_id, steps))
        print(result)

