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
from isaaclab.managers import SceneEntityCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass

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


def run_simulator(sim: sim_utils.SimulationContext, scene: InteractiveScene):
    
    robot = scene["robot"]

    robot_entity_cfg = SceneEntityCfg("robot", joint_names=[".*"], body_names=[".*"])

    robot_entity_cfg.resolve(scene)

    sim_dt = sim.get_physics_dt()

    joint_position = robot.data.default_joint_pos.clone()
    joint_vel = robot.data.default_joint_vel.clone()
    robot.write_joint_state_to_sim(joint_position, joint_vel)

    while simulation_app.is_running():

        # joint_position = robot.data.default_joint_pos.clone()
        # print(joint_position)
        # joint_vel = robot.data.default_joint_vel.clone()
        # robot.write_joint_state_to_sim(joint_position, joint_vel)
        
        joint_position_list = [[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        joint_position = torch.tensor(joint_position_list[0], device=sim.device)

        robot.reset()
        joint_pos_des = joint_position.unsqueeze(0)[:, robot_entity_cfg.joint_ids].clone()
        robot.set_joint_position_target(joint_pos_des, joint_ids=robot_entity_cfg.joint_ids)
        scene.write_data_to_sim()

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