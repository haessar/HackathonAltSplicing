# HackathonAltSplicing

![image](https://github.com/user-attachments/assets/3f94eb52-b412-4ec2-96fc-67f5e3fb34d3)

## Contributing

### 🔖 Issue Labelling

I've created issues that reflect the work packages that I outlined in the introductory slides (for some of them it made sense to split them in two). Work package #1 is signified by `(WP1)`, etc. I've used labels to designate which "theme" they belong to, whether they have a significant MARS component, and whether they are `Coding` or `Research` heavy. When determining what you want to work on, you can filter the labels that appeal to you or are a suitable match to your skillset (e.g. if you have no interest in using MARS, you could filter out the `MARS` label).

### 🔀 Branching Strategy

As there will be lots of us working feverishly in the same repo, I recommend we use **feature branches** for all development work rather than `main`.  

- Create a new branch from `main` for each new feature or fix (perhaps to work on a GitHub issue):  
  ```bash
  git checkout -b your-feature-name
  ```
- Once you're happy with changes, open a pull request to merge into `main` and someone can review them.

- This will help prevent conflicts, support collaboration, and maintain a clean commit history.
