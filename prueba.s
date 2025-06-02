.data
global_data:
r: .word 0

.text
incr:
	la $gp, global_data	# Inicializar $gp a sección .data
	lw $t0, x($gp)	# Cargar variable x
	move $t1, $t0	# Guardar operando izquierdo
	li $t0, 1	# Cargar constante 1
	add $t0, $t1, $t0	# Suma
	move $v0, $t0	# Retornar valor
	jr $ra	# Regresar de función
main:
	la $gp, global_data	# Inicializar $gp a sección .data
	li $t0, 5	# Cargar constante 5
	subu $sp, $sp, 4	# Reservar espacio en pila
	sw $t0, 0($sp)	# Push argumento
	jal incr	# Llamar función incr
	move $t0, $v0	# Resultado en $t0
	addu $sp, $sp, 4	# Limpiar pila
	sw $t0, r($gp)	# Asignar a r
	lw $t0, r($gp)	# Cargar variable r
	move $a0, $t0	# Pasar arg. a $a0
	li $v0, 1	# Imprimir entero
	syscall
	li $v0, 10
	syscall
