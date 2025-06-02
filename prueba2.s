.data
newline: .asciiz "\n"
i: .word 0
r: .word 0

.text
j main
.globl main

incr:
	move $t0, $a0	# param 'x' (en $a0) → $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 1	# const 1
	add $t0, $t1, $t0	# suma
	move $v0, $t0	# valor de retorno en $v0
	jr $ra	# retornar de incr
	jr $ra	# retornar de incr
main:
	li $t0, 10	# const 10
	la $t1, r	# cargar dirección de r
	sw $t0, 0($t1)	# almacenar $t0 → r
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	li $t0, 0	# const 0
	la $t1, i	# cargar dirección de i
	sw $t0, 0($t1)	# almacenar $t0 → i
while0:
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 10	# const 10
	slt $t0, $t1, $t0	# menor que
	beq $t0, $zero, endwhile1	# condición falsa → fin while
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $a0, $t0	# pasar argumento a $a0
	jal incr	# llamar incr
	move $t0, $v0	# resultado de incr → $t0
	la $t1, i	# cargar dirección de i
	sw $t0, 0($t1)	# almacenar $t0 → i
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 5	# const 5
	slt $t0, $t1, $t0	# menor que
	beq $t0, $zero, else2	# condición falsa → else
	la $t1, r	# cargar dirección de r
	lw $t0, 0($t1)	# cargar r en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 25	# const 25
	add $t0, $t1, $t0	# suma
	la $t1, r	# cargar dirección de r
	sw $t0, 0($t1)	# almacenar $t0 → r
	j endif3	# saltar fin if
else2:
	la $t1, i	# cargar dirección de i
	lw $t0, 0($t1)	# cargar i en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 5	# const 5
	seq $t0, $t1, $t0	# igual
	beq $t0, $zero, else4	# condición falsa → else
	la $t1, r	# cargar dirección de r
	lw $t0, 0($t1)	# cargar r en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 35	# const 35
	sub $t0, $t1, $t0	# resta
	la $t1, r	# cargar dirección de r
	sw $t0, 0($t1)	# almacenar $t0 → r
	j endif5	# saltar fin if
else4:
	la $t1, r	# cargar dirección de r
	lw $t0, 0($t1)	# cargar r en $t0
	move $t1, $t0	# guardar op izq en $t1
	li $t0, 1	# const 1
	sub $t0, $t1, $t0	# resta
	la $t1, r	# cargar dirección de r
	sw $t0, 0($t1)	# almacenar $t0 → r
endif5:
endif3:
	j while0	# volver a condición
endwhile1:
	la $t1, r	# cargar dirección de r
	lw $t0, 0($t1)	# cargar r en $t0
	move $a0, $t0	# pasar valor a $a0 para print_int
	li   $v0, 1	# syscall print_int
	syscall
	la   $a0, newline	# cargar dirección de "\n"
	li   $v0, 4	# syscall print_string
	syscall
	li   $t0, 0	# output devuelve 0
	li $v0, 10	# exit por defecto
	syscall
