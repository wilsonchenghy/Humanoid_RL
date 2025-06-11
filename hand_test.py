import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Humanoid Hand Testing")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.controllers import DifferentialIKController, DifferentialIKControllerCfg
from isaaclab.managers import SceneEntityCfg
from isaaclab.markers import VisualizationMarkers
from isaaclab.markers.config import FRAME_MARKER_CFG
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR
from isaaclab.utils.math import subtract_frame_transforms

from HumanoidRL.HumanoidRLPackage.HumanoidRLSetup.modelCfg.universal_robots import UR10_CFG
from HumanoidRL.HumanoidRLPackage.HumanoidRLSetup.modelCfg.franka import FRANKA_PANDA_HIGH_PD_CFG
from HumanoidRL.HumanoidRLPackage.HumanoidRLSetup.modelCfg.humanoid import HAND_CFG

from isaaclab.utils.assets import ISAACLAB_NUCLEUS_DIR



@configclass
class HandSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -1.05)),
    )

    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75))
    )

    # table = AssetBaseCfg(
    #     prim_path="{ENV_REGEX_NS}/Table",
    #     spawn=sim_utils.UsdFileCfg(
    #         usd_path=f"{ISAAC_NUCLEUS_DIR}/Props/Mounts/Stand/stand_instanceable.usd", scale=(1.0, 1.0, 1.0)
    #     ),
    # )

    robot = HAND_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    # robot1 = UR10_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    # robot = FRANKA_PANDA_HIGH_PD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


def run_simulator(sim: sim_utils.SimulationContext, scene: InteractiveScene):
    
    # robot = scene["robot"]

    # robot_entity_cfg = SceneEntityCfg("robot", joint_names=[".*"], body_names=["ee_link"])
    # robot_entity_cfg = SceneEntityCfg("robot", joint_names=["panda_joint.*"], body_names=["panda_hand"])

    # robot_entity_cfg.resolve(scene)

    sim_dt = sim.get_physics_dt()

    while simulation_app.is_running():

        # joint_position = robot.data.default_joint_pos.clone()
        # print(joint_position)
        # joint_vel = robot.data.default_joint_vel.clone()
        # robot.write_joint_state_to_sim(joint_position, joint_vel)

        sim.step()

        scene.update(sim_dt)


def main():
    sim_cfg = sim_utils.SimulationCfg(dt=0.01, device=args_cli.device)
    sim = sim_utils.SimulationContext(sim_cfg)

    sim.set_camera_view([2.5, 2.5, 2.5], [0.0, 0.0, 0.0])

    scene_cfg = HandSceneCfg(num_envs=1, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)

    sim.reset()

    print("[INFO]: Setup complete...")

    run_simulator(sim, scene)


if __name__ == "__main__":
    main()
    simulation_app.close()


# (env_isaaclab) hy@hy-LOQ-15IRX9:~/Downloads/Humanoid$ PYTHONPATH=$(pwd) /home/hy/IsaacLab/isaaclab.sh -p hand_test.py 