(define (domain sokoban)
(:requirements :typing)
(:types LOC DIR BOX)
(:predicates 
             (at-robot ?l - LOC)
             (at ?o - BOX ?l - LOC)
             (adjacent ?l1 - LOC ?l2 - LOC ?d - DIR) 
             (clear ?l - LOC)
)

(:action movebox
	:parameters (?from - LOC ?to - LOC ?b - BOX)
	:precondition (and (clear ?to) (at ?b ?from))
	:effect (and (at ?b ?to) (not (at ?b ?from))))

)