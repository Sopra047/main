import random
from pyrogram import Client, filters, enums
from info import COMMAND_HAND_LER
from plugins.helper_functions.cust_p_filters import f_onw_fliter


RUN_STRINGS = (
     "La vie c'est des étapes... La plus douce c'est l'amour... La plus dure c'est la séparation... La plus pénible c'est les adieux... La plus belle c'est les retrouvailles. Citation Amour & Vie",
     "Exige beaucoup de toi-même et attends peu des autres. Ainsi beaucoup d'ennuis te seront épargnés. Confucius",
     "Je t'aime éperdument, et je te le dis, et je te le répète, et mes paroles te l'expriment, et mes baisers te le prouvent, et quand j'ai fini... je recommence. Je voudrais recommencer ainsi pendant l'éternité, et chaque soir, je regrette la nuit qui va s'écouler sans toi, et chaque matin, j'en veux au soleil de briller, comme aujourd'hui, quand tu n'es pas dans mes bras. Victor Hugo",
     "Dans la vie on ne fait pas ce que l'on veut mais on est responsable de ce que l'on est. Jean-Paul Sartre",
     "La vie est un mystère qu'il faut vivre, et non un problème à résoudre. Gandhi",
     "Le travail éloigne de nous trois grands maux : l'ennui, le vice et le besoin. Voltaire",
     "La vie, c'est comme une bicyclette, il faut avancer pour ne pas perdre l'équilibre. Albert Einstein",
     "Choisissez un travail que vous aimez et vous n'aurez pas à travailler un seul jour de votre vie. Confucius",
     "Pour critiquer les gens il faut les connaître, et pour les connaître, il faut les aimer. Coluche",
     "Tout le monde est un génie. Mais si vous jugez un poisson à sa capacité de grimper à un arbre, il vivra toute sa vie en croyant qu'il est stupide. Albert Einstein",
     "Que la force me soit donnée de supporter ce qui ne peut être changé et le courage de changer ce qui peut l'être mais aussi la sagesse de distinguer l'un de l'autre. Marc Aurèle",
     "L'éducation est l'arme la plus puissante qu'on puisse utiliser pour changer le monde. Nelson Mandela",
     "La règle d'or de la conduite est la tolérance mutuelle, car nous ne penserons jamais tous de la même façon, nous ne verrons qu'une partie de la vérité et sous des angles différents. Gandhi",
     "On a deux vies. La deuxième commence quand on réalise qu'on n'en a qu'une. Confucius",
     "La chose la plus triste à propos de la trahison est qu'elle ne vient jamais d'ennemis, elle vient de ceux en qui vous avez le plus confiance. XXXTentacion",
     "La valeur d'un homme ne se mesure pas à son argent, son statut ou ses possessions. La valeur d'un homme réside dans sa personnalité, sa sagesse, sa créativité, son courage, son indépendance et sa maturité. Mark W. B. Brinton",
     "La folie, c'est se comporter de la même manière et s'attendre à un résultat différent. Albert Einstein",
     "Il ne faut avoir aucun regret pour le passé, aucun remords pour le présent, et une confiance inébranlable pour l'avenir. Jean Jaurès",
     "La vie, ce n'est pas d'attendre que les orages passent, c'est d'apprendre à danser sous la pluie. Sénèque!",
     "Les vrais amis sont comme les étoiles, on ne les voit pas tout le temps, mais ils sont toujours là.",
     "Croyez en vos rêves et ils se réaliseront peut-être. Croyez en vous et ils se réaliseront sûrement. Martin Luther King",
     "C'est dans l'effort que l'on trouve la satisfaction et non dans la réussite. Un plein effort est une pleine victoire. Gandhi",
     "Il n'existe que deux choses infinies, l'univers et la bêtise humaine... mais pour l'univers, je n'ai pas de certitude absolue. Albert Einstein",
     "Le pire ennemi du marin, ce n'est pas la tempête qui fait rage ; ce n'est pas la vague écumante qui s'abat sur le pont, emportant tout sur son passage ; ce n'est pas le récif perfide caché à fleur d'eau et qui déchire le flanc du navire ; le pire ennemi du marin, c'est l'alcool ! Hergé",
     "Agis avec gentillesse, mais n'attends pas de la reconnaissance. Confucius",
     "Les gens faibles se vengent. Les gens forts pardonnent. Les gens intelligents ignorent. Albert Einstein",
     "Il faudrait essayer d'être heureux, ne serait-ce que pour donner l'exemple. Jacques Prévert",
     "Le courage n'est pas l'absence de peur, mais la capacité de vaincre ce qui fait peur. Nelson Mandela",
)


@Client.on_message(
    filters.command("runs", COMMAND_HAND_LER) &
    f_onw_fliter
)
async def runs(_, message):
    """ /runs strings """
    effective_string = random.choice(RUN_STRINGS)
    if message.reply_to_message:
        await message.reply_to_message.reply_text(effective_string)
    else:
        await message.reply_text(effective_string)
