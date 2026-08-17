.text
.globl opencuda_asm_cpu_relax
.type opencuda_asm_cpu_relax, %function
opencuda_asm_cpu_relax:
    yield
    ret
.size opencuda_asm_cpu_relax, .-opencuda_asm_cpu_relax
