import os
import sys

import numpy as np
import supersuit as ss
from array2gif import write_gif
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.preprocessing import (
    is_image_space,
    is_image_space_channels_first,
)
from stable_baselines3.common.vec_env import VecMonitor, VecNormalize, VecTransposeImage

os.environ["SDL_VIDEODRIVER"] = "dummy"
num = sys.argv[1]

from social_dilemmas.envs import pettingzoo_env

env_name = "harvest"
n_agents = 5
num_frames = 4

env = pettingzoo_env.env(
    env=env_name,
    num_agents=n_agents,
)
env = ss.observation_lambda_v0(env, lambda x, _: x["curr_obs"], lambda s: s["curr_obs"])
env = ss.frame_stack_v1(env, num_frames)

policies = os.listdir("./mature_policies/" + str(num) + "/")

for policy in policies:
    model = PPO.load("./mature_policies/" + str(num) + "/" + policy)

    obs_list = []
    i = 0
    env.reset()

    while True:
        for agent in env.agent_iter():
            observation, _, done, _ = env.last()
            action = (
                model.predict(observation, deterministic=True)[0] if not done else None
            )

            env.step(action)
            i += 1
            if i % (len(env.possible_agents) + 1) == 0:
                obs_list.append(
                    np.transpose(env.render(mode="rgb_array"), axes=(1, 0, 2))
                )

        break

    print("writing gif")
    write_gif(
        obs_list, "./mature_gifs/" + num + "_" + policy.split(".")[0] + ".gif", fps=5
    )

env.close()