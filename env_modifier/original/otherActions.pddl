(define (domain grid)
(:requirements :strips :typing)
(:types place shape key)
(:predicates (conn ?x ?y - place)
             (key-shape ?k - key ?s - shape)
             (lock-shape ?x - place ?s - shape)
             (at ?r - key ?x - place )
       (at-robot ?x - place)
             (locked ?x - place)
             (carrying ?k - key)
             (open ?x - place)
)


;;; (:action connect
;;; :parameters (?place1 ?place2 - place)
;;; :precondition (and (not (conn ?place1 ?place2)) (not (conn ?place2 ?place1)) )
;;; :effect (and (conn ?place1 ?place2) (conn ?place2 ?place1) )
;;; )


(:action disconnect
:parameters (?place1 ?place2 - place)
:precondition (and (conn ?place1 ?place2) (conn ?place2 ?place1) )
:effect (and (not (conn ?place1 ?place2)) (not (conn ?place2 ?place1)) )
))





