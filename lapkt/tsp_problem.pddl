
;; TSP PDDL ***Problem File*** 

    (define (problem tsp-01)
    (:domain tsp)
    (:objects Sydney Adelade Brisbane Perth Darwin - node)

    ;; Define the initial situation
    (:init  (connected Sydney Brisbane)
            (connected Brisbane Sydney)
            (connected Adelade Sydney)
            (connected Sydney Adelade)
            (connected Adelade Perth)
            (connected Perth Adelade)
            (connected Adelade Darwin)
            (connected Darwin Adelade)
            (at Sydney)
    )
    (:goal
            (and 
                (at Sydney)
                (visited Sydney)
                (visited Adelade)
                (visited Brisbane)
                (visited Perth)
                (visited Darwin)
            )
    )
    )
