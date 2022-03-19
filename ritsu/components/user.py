"""Holds commands which can be performed on users"""

import hikari
import tanjun


@tanjun.with_user_slash_option("user", "The user", default=None)
@tanjun.as_slash_command("userinfo", "To fetch information about a user")
async def cmd_userinfo(ctx: tanjun.abc.SlashContext, user: hikari.User | hikari.InteractionMember) -> None:
    if user is None:
        user: hikari.InteractionMember = ctx.member

    await ctx.create_initial_response(
        embed=(
            hikari.Embed(title="User information", color=0xF6CEE7)
            .set_thumbnail(user.avatar_url)
            .add_field("Joined on", f"<t:{int(user.joined_at.timestamp())}:f>", inline=True)
            .add_field("Created on", f"<t:{int(user.user.created_at.timestamp())}:f>", inline=True)
        )
    )

comp_user: tanjun.Component = tanjun.Component(name="comp_user").load_from_scope()
comp_user.make_loader()

__all__: tanjun.typing.Final[list[str]] = ['comp_user']
