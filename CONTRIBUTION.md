First make a new branch with the name of your feature all in one word. e.g `wizard-spells`

```bash
cd ~/code/untangled-2017
git checkout -b wizard-spells
```

Next, make your code changes!

*...some time later...*

Save your code changes with a message
```bash
git add -A
git commit -m "Added my awesome new spell"
```

Push your code changes

```bash
git push origin wizard-spells
```

Make a pull request

Open the pull requests: https://github.com/neontribe/untangled-2017/pulls

Click 'New pull request'

Change the 'compare: master' to 'compare: wizard-spells'

Create the pull request
