import { supabase } from "./supabase";

/* =========================================================
   GET CURRENT USER
========================================================= */

async function getCurrentUser() {
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error) {
    throw error;
  }

  if (!user) {
    throw new Error("You must be signed in to use Saved Papers.");
  }

  return user;
}


/* =========================================================
   GET SAVED PAPERS
========================================================= */

export async function getSavedPapers() {
  const user = await getCurrentUser();

  const { data, error } = await supabase
    .from("saved_papers")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", {
      ascending: false,
    });

  if (error) {
    throw error;
  }

  return data || [];
}


/* =========================================================
   SAVE PAPER
========================================================= */

export async function savePaper(paper) {
  const user = await getCurrentUser();

  const { data, error } = await supabase
    .from("saved_papers")
    .insert({
      user_id: user.id,

      paper_id: String(paper.id),

      title: paper.title,

      category:
        paper.category || null,

      author:
        paper.author || null,

      description:
        paper.description || null,

      year:
        paper.year
          ? String(paper.year)
          : null,

      pages:
        paper.pages || null,

      pdf_url:
        paper.pdf_url || null,
    })
    .select()
    .single();

  if (error) {
    /*
     * PostgreSQL unique violation.
     * The same user cannot save the same paper twice.
     */
    if (error.code === "23505") {
      return null;
    }

    throw error;
  }

  return data;
}


/* =========================================================
   REMOVE SAVED PAPER
========================================================= */

export async function removeSavedPaper(paperId) {
  const user = await getCurrentUser();

  const { error } = await supabase
    .from("saved_papers")
    .delete()
    .eq("user_id", user.id)
    .eq(
      "paper_id",
      String(paperId)
    );

  if (error) {
    throw error;
  }

  return true;
}


/* =========================================================
   CHECK IF PAPER IS SAVED
========================================================= */

export async function isPaperSaved(paperId) {
  const user = await getCurrentUser();

  const { data, error } = await supabase
    .from("saved_papers")
    .select("id")
    .eq("user_id", user.id)
    .eq(
      "paper_id",
      String(paperId)
    )
    .maybeSingle();

  if (error) {
    throw error;
  }

  return Boolean(data);
}