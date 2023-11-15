My CS final project is a new programming language called Narrate. Narrate is an
interpreted domain-specific scripting language designed for creating text-based
adventure games. Here's an example of what Narrate source code looks like:
```
@module dungeon:

@scene wake-up-in-dungeon:
  # This is a comment.
  # A scene may have one "flavortext" directive. This contains text to be
  # printed before presenting the scene's options.
  flavortext {
    You wake up in a dark, musty dungeon.
    There's very little light except for a high-placed window with bars.
    Your head hurts terribly; you don't know why.
  };

  # A scene must have a "select" directive. This lists the options that a
  # player can choose interactively. The player chooses options by their index.
  select {
    "Look out the window" => look-out-window,
    "Blindly search your cell" => find-hidden-map,
    "Cry" => get-yelled-at-by-guards
  };
@end-scene

@scene find-hidden-map:
  # The player has an "inventory" which is a global container of strings.
  # Items can be added to the inventory with the "get" directive and removed
  # with the "lose" directive. Inventory items are case-insensitive.
  get "Waterlogged treasure map";

  flavortext {
    You search around your cell by touch. Finally, looking under the pile
    of straw that makes your bedding, you find a piece of paper that feels
    like it got wet and dried out.
  };

  select {
    # Options can be made conditional with the "has" keyword. These options
    # will only be made visible if the predicate of "has" is a string present
    # in the player's inventory.
    has "Golden key" ? "Try to make a run for it" => try-to-escape,

    # Scenes defined in another file can be referenced like so.
    # The file is lazily loaded.
    "Try to figure out where you are" => @file("./foo.nar")::dungeon::use-map-to-locate-self
  };
@end-scene

@end-module dungeon
```
An interactive session with that code might look like this:
```
You wake up in a dark, musty dungeon.
There's very little light except for a high-placed window with bars.
Your head hurts terribly; you don't know why.
Options:
[1] Look out the window
[2] Blindly search your cell
[3] Cry
Choose: 2

You search around your cell by touch. Finally, looking under the pile
of straw that makes your bedding, you find a piece of paper that feels
like it got wet and dried out.
Options:
[1] Try to figure out where you are
Choose:
```
