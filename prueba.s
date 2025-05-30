.data
global_data:
  a: .word 0, 0, 0, 0, 0
  i: .word 0

.text
main:
	la $gp, global_data	# Inicializar $gp a global_data
	li $t0, 0	# Cargar constante 0
	sw $t0, 20($gp)	# Asignar a i
	li $t0, 0	# Cargar constante 0
	sw $t0, 20($gp)	# Asignar a i
	li $v0, 10	# exit
	syscall
