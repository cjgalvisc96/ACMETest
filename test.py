if __name__ == '__main__':
    conditions_results = [True,True,True,False]
    result = all(
        condition_result is True for condition_result in
        conditions_results
    )
    print((result))
