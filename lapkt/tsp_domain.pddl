
;; TSP PDDL ***Domain File*** 

    (define (domain tsp)
        (:requirements :typing)
        (:types node)

        ;; Define the facts in the problem
        ;; "?" denotes a variable, "-" a type
        (:predicates 
            (move ?from ?to - node)
            (at ?pos - node)
            (connected ?start ?end - node)
            (visited ?end - node)
        )

        ;; Define the action(s)
        (:action move
            :parameters (?start ?end - node)
            :precondition (and 
                (at ?start)
                (connected ?start ?end)
            )
            :effect (and 
                (at ?end)
                (visited ?end)
                (not (at ?start))
            )
        )
    )
