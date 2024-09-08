import builtins
import os
import sys
import time

from clsACOSCP import clsACOSCP

# Guardar la función print original
original_print = print

# Redefinir print para que siempre use flush=True
def custom_print(*args, **kwargs):
    kwargs['flush'] = True
    return original_print(*args, **kwargs)

# Reemplazar la función print
builtins.print = custom_print

def run_acoscp(instance_file, results_dir, alpha, beta, rho, q0, iters, ants, initial_value):
    objACOSCP = clsACOSCP()

    # Set ACO parameters
    objACOSCP.setAlpha(alpha)
    objACOSCP.setBeta(beta)
    objACOSCP.setRho(rho)
    objACOSCP.setQ0(q0)
    objACOSCP.setInitialValue(initial_value)
    objACOSCP.setNbrOfIters(iters)
    objACOSCP.setNbrOfAnts(ants)

    # Set execution parameters
    instance_dir, instance_name = os.path.split(instance_file)

    objACOSCP.setInstanceName(instance_name)
    objACOSCP.setInstanceDir(f"{instance_dir}/")
    objACOSCP.setResultDir(f"{results_dir}/")

    print(f"Leyendo instancia...")
    objACOSCP.readInstance()

    print(f"Comenzando a resolver ACOSCP...")
    start_time = time.time()

    objACOSCP.solveProblem()
    print(f"Terminó la ejecución de ACOSCP.")
    print(f"Tiempo total de ejecución: {int((time.time() - start_time)/60)} minutos")

if __name__ == "__main__":
    
    if len(sys.argv) != 10:
        print("Error: No se pasaron los parámetros necesarios")
        print("Usar: python acoscp_wrapper.py <instance_file> <results_dir> <alpha> <beta> <rho> <q0> <iters> <ants> <initial_value>")
        sys.exit(1)

    instance_file = sys.argv[1]
    results_dir = sys.argv[2]
    alpha = float(sys.argv[3])
    beta = float(sys.argv[4])
    rho = float(sys.argv[5])
    q0 = float(sys.argv[6])
    iters = int(sys.argv[7])
    ants = int(sys.argv[8])
    initial_value = float(sys.argv[9])

    run_acoscp(instance_file, results_dir, alpha, beta, rho, q0, iters, ants, initial_value)