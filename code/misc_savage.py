def savage():
	import random
	
	insults = """You do realize that people just *tolerate* you, right?
You're not pretty enough to be this stupid...
Your mum is so fat that even Dora couldn't explore her.
Take that mask off, Halloween isn't until October!
I'm surprised the army hasn't hired you already; your face kills faster than any gun or bomb.
Do aliens exist? Wait, that's a stupid question, I'm looking at one right now.
You must have been born on a highway because that's where most accidents happen.
You're so ugly when your mum picked you up from school and dropped you at home, she got arrested for littering.
Your face will be the reason for human extinction.
You are so poor that you run after a garbage truck with a shopping list.
Anyone who ever loved you was wrong.
If you were anymore inbred you would be a sandwich.
Now I know why everybody talks about you behind your back.
If I wanted to kill myself, I’d climb to your ego and jump to your IQ.
I can explain it to you, but I can’t understand it for you.
You are one of those people who would be enormously improved by death.
your gene pool could use a little chlorine
you couldn’t pour water out of a boot if the instructions were on the sole.
You look like a before picture.
You coffin dodging oxygen thief.
You’re like the top piece of bread. Everybody touches you, but nobody wants you.
I treasure the time i don’t spend with you.
What is that you are wearing? Looks like a dog took a shit on a knitted jumper.
What's the different between you and Hitler? At least Hitler knew when to kill himself.
Don't play hard to get when you're hard to want.
Your bacteria is the only culture you have.
The only good thing to pull itself out of your mom's vagina was your dad's dick. Too bad it wasnt fast enough.
I doubt that you could drown: fat floats.
Whats the difference between breathing in paint and talking to you? Breathing in paint kills less brain cells
Youre like meat at a butcher shop: you could use a good hanging
You clearly have not been burdened by an overabundance of education
You will be utterly forgotten
“Bless your heart.” Southern code for “you’re a fucking retard.”
What doesn’t kill you…disappoints me.
The best part of you ran down your mother’s legs"""
	text = insults.splitlines()
	message = (text[random.randint(0, (len(text)) - 1)])
	return message